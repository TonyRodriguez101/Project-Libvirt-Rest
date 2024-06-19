from flask import Flask, request, jsonify
import libvirt
import os
import requests
import uuid

app = Flask(__name__)

def connect_libvirt():
    return libvirt.open('qemu:///system')

def ensure_iso_exists(iso_url, iso_path):
    if not os.path.exists(iso_path):
        response = requests.get(iso_url, stream=True)
        if response.status_code == 200:
            with open(iso_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            return True
        else:
            return False
    return True


#-------------------------------------------------
# Others ISOs_URL and ISO_PATH
# ISO_URL = 'https://releases.ubuntu.com/20.04.3/ubuntu-20.04.3-live-server-amd64.iso'
# ISO_PATH = '/var/lib/libvirt/images/ubuntu-20.04.3-live-server-amd64.iso'

# ISO_URL = 'https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-11.1.0-amd64-netinst.iso'
# ISO_PATH = '/var/lib/libvirt/images/debian-11.1.0-amd64-netinst.iso'  

# Ubuntu 22.04.4   ISO
ISO_URL = 'https://mirror.leitecastro.com/ubuntu-releases/22.04.4/ubuntu-22.04.4-desktop-amd64.iso'
ISO_PATH = '/var/lib/libvirt/images/ubuntu-22.04.4-desktop-amd64.iso'



# ISO_URL = 'https://dl-cdn.alpinelinux.org/alpine/v3.20/releases/x86_64/alpine-standard-3.20.1-x86_64.iso'
# ISO_PATH = '/var/lib/libvirt/images/alpine-standard-3.20.1-x86_64.iso'

def create_disk_image(disk_path, size_gb):
    os.system(f'qemu-img create -f qcow2 {disk_path} {size_gb}G') 

def generate_vm_xml(vm_name, disk_path):
    return f"""
    <domain type='kvm'>
      <name>{vm_name}</name>
      <memory unit='KiB'>4194304</memory> --> 4GB
      <vcpu placement='static'>3</vcpu> --> 3 cores
      <os>
        <type arch='x86_64' machine='pc-i440fx-2.9'>hvm</type> --> x86_64 architecture and hvm type
        <boot dev='cdrom'/> --> boot from cdrom 
      </os>
      <devices>
        <disk type='file' device='disk'> --> disk type file and device disk
          <driver name='qemu' type='qcow2'/> --> driver name qemu and type qcow2
          <source file='{disk_path}'/> 
          <target dev='vda' bus='virtio'/> --> target device vda and bus virtio  
        </disk>
        <disk type='file' device='cdrom'> 
          <driver name='qemu' type='raw'/> 
          <source file='{ISO_PATH}'/>  --> source file iso path
          <target dev='hdc' bus='ide'/>
          <readonly/>  --> read only
        </disk>
        <interface type='network'> 
          <mac address='52:54:00:{uuid.uuid4().hex[:2]}:{uuid.uuid4().hex[:2]}:{uuid.uuid4().hex[:2]}'/> --> mac address
          <source network='default'/> 
          <model type='virtio'/> 
        </interface>
        <graphics type='vnc' port='-1' autoport='yes'/> 
      </devices>
    </domain>
    """

@app.route('/vms', methods=['POST'])
def create_vm():
    vm_name = request.json.get('name', f'vm-{uuid.uuid4()}')
    disk_path = f'/var/lib/libvirt/images/{vm_name}.qcow2'

    # Ensure ISO exists
    if not ensure_iso_exists(ISO_URL, ISO_PATH):
        return 'Failed to download ISO', 500

    # Create a new disk image
    create_disk_image(disk_path, 30)  # Create a 40GB disk image

    # Generate VM XML configuration
    config_xml = generate_vm_xml(vm_name, disk_path) 

    conn = connect_libvirt()
    try:
        conn.createXML(config_xml, 0)
        conn.close()
        return 'VM created', 201
    except libvirt.libvirtError as e:
        conn.close()
        return f'Failed to create VM: {str(e)}', 400

#-------------------------------------------------
# List VMs
@app.route('/vms', methods=['GET'])
def list_vms():
    conn = connect_libvirt()
    domains = conn.listAllDomains()
    vms = []
    for domain in domains:
        vms.append({
            'id': domain.ID(),
            'name': domain.name(),
            'state': domain.state()[0]
        })
    conn.close()
    return jsonify(vms)

#-------------------------------------------------
# Delete VM
@app.route('/vms/<vm_name>', methods=['DELETE'])
def delete_vm(vm_name):
    conn = connect_libvirt()
    domain = conn.lookupByName(vm_name)
    if domain:
        domain.undefine()
        if domain.isActive():
            domain.destroy()
        conn.close()
        # Optionally delete the disk file
        disk_path = f'/var/lib/libvirt/images/{vm_name}.qcow2'
        if os.path.exists(disk_path):
            os.remove(disk_path)
        return 'VM deleted', 204
    else:
        conn.close()
        return 'VM not found', 404

#-------------------------------------------------
# Start VM
@app.route('/vms/<vm_name>/start', methods=['POST'])
def start_vm(vm_name):
    conn = connect_libvirt()
    domain = conn.lookupByName(vm_name)
    if domain:
        domain.create()
        conn.close()
        return 'VM started', 200
    else:
        conn.close()
        return 'VM not found', 404

#-------------------------------------------------
# Stop VM
@app.route('/vms/<vm_name>/stop', methods=['POST'])
def stop_vm(vm_name):
    conn = connect_libvirt()
    domain = conn.lookupByName(vm_name)
    if domain:
        domain.shutdown()
        conn.close()
        return 'VM stopped', 200
    else:
        conn.close()
        return 'VM not found', 404

#-------------------------------------------------
# Extraction of VM XML data configuration
@app.route('/vms/<vm_name>/xml', methods=['GET'])
def get_vm_xml(vm_name):
    conn = connect_libvirt()
    domain = conn.lookupByName(vm_name)
    if domain:
        xml = domain.XMLDesc(0)
        conn.close()
        return xml, 200
    else:
        conn.close()
        return 'VM not found', 404

if __name__ == '__main__':
    app.run(debug=True)
