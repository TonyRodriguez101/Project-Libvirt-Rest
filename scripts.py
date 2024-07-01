from flask import Flask, request, jsonify, Response
import libvirt
import os
import uuid
import threading
import subprocess
import tarfile
from pathlib import Path

app = Flask(__name__)

def connect_libvirt():
    return libvirt.open('qemu:///system')

#-------------------------------------------------
# Create VM
#-------------------------------------------------
def ensure_iso_exists(iso_url, iso_path):
    # Verifica si el ISO existe y descárgalo si es necesario
    if not os.path.exists(iso_path):
        subprocess.run(['wget', iso_url, '-O', iso_path], check=True)
    return os.path.exists(iso_path)

def create_disk_image(disk_path, disk_size_gb):
    # Crea una imagen de disco
    subprocess.run(['qemu-img', 'create', '-f', 'qcow2', disk_path, f'{disk_size_gb}G'], check=True)

def generate_vm_xml(vm_name, disk_path, iso_path, memory_mb, vcpu_count):
    mac_address = f'52:54:00:{uuid.uuid4().hex[:2]}:{uuid.uuid4().hex[:2]}:{uuid.uuid4().hex[:2]}'
    return f"""
    <domain type='kvm'>
        <name>{vm_name}</name>
        <uuid>{uuid.uuid4()}</uuid>
        <memory unit='KiB'>{memory_mb * 1024}</memory>
        <currentMemory unit='KiB'>{memory_mb * 1024}</currentMemory>
        <vcpu placement='static'>{vcpu_count}</vcpu>
        <os>
            <type arch='x86_64' machine='pc-q35-6.2'>hvm</type>
            <boot dev='cdrom'/>
        </os>
        <features>
            <acpi/>
            <apic/>
            <vmport state='off'/>
        </features>
        <cpu mode='host-passthrough' check='none' migratable='on'/>
        <clock offset='utc'>
            <timer name='rtc' tickpolicy='catchup'/>
            <timer name='pit' tickpolicy='delay'/>
            <timer name='hpet' present='no'/>
        </clock>
        <on_poweroff>destroy</on_poweroff>
        <on_reboot>restart</on_reboot>
        <on_crash>destroy</on_crash>
        <pm>
            <suspend-to-mem enabled='no'/>
            <suspend-to-disk enabled='no'/>
        </pm>
        <devices>
            <emulator>/usr/bin/qemu-system-x86_64</emulator>
            <disk type='file' device='disk'>
                <driver name='qemu' type='qcow2' discard='unmap'/>
                <source file='{disk_path}' index='1'/>
                <backingStore/>
                <target dev='vda' bus='virtio'/>
                <alias name='virtio-disk0'/>
                <address type='pci' domain='0x0000' bus='0x04' slot='0x00' function='0x0'/>
            </disk>
            <disk type='file' device='cdrom'>
                <driver name='qemu'/>
                <source file='{iso_path}'/>
                <target dev='sda' bus='sata'/>
                <readonly/>
                <alias name='sata0-0-0'/>
                <address type='drive' controller='0' bus='0' target='0' unit='0'/>
            </disk>
            <controller type='usb' index='0' model='qemu-xhci' ports='15'>
                <alias name='usb'/>
                <address type='pci' domain='0x0000' bus='0x02' slot='0x00' function='0x0'/>
            </controller>
            <controller type='pci' index='0' model='pcie-root'>
                <alias name='pcie.0'/>
            </controller>
            <controller type='pci' index='1' model='pcie-root-port'>
                <model name='pcie-root-port'/>
                <target chassis='1' port='0x10'/>
                <alias name='pci.1'/>
                <address type='pci' domain='0x0000' bus='0x00' slot='0x02' function='0x0' multifunction='on'/>
            </controller>
            <controller type='sata' index='0'>
                <alias name='ide'/>
                <address type='pci' domain='0x0000' bus='0x00' slot='0x1f' function='0x2'/>
            </controller>
            <interface type='network'>
                <mac address='{mac_address}'/>
                <source network='default' portid='{uuid.uuid4()}' bridge='virbr0'/>
                <target dev='vnet2'/>
                <model type='virtio'/>
                <alias name='net0'/>
                <address type='pci' domain='0x0000' bus='0x01' slot='0x00' function='0x0'/>
            </interface>
            <serial type='pty'>
                <source path='/dev/pts/2'/>
                <target type='isa-serial' port='0'>
                    <model name='isa-serial'/>
                </target>
                <alias name='serial0'/>
            </serial>
            <console type='pty' tty='/dev/pts/2'>
                <source path='/dev/pts/2'/>
                <target type='serial' port='0'/>
                <alias name='serial0'/>
            </console>
            <channel type='unix'>
                <source mode='bind' path='/var/lib/libvirt/qemu/channel/target/domain-2-{vm_name}/org.qemu.guest_agent.0'/>
                <target type='virtio' name='org.qemu.guest_agent.0' state='disconnected'/>
                <alias name='channel0'/>
                <address type='virtio-serial' controller='0' bus='0' port='1'/>
            </channel>
            <channel type='spicevmc'>
                <target type='virtio' name='com.redhat.spice.0' state='disconnected'/>
                <alias name='channel1'/>
                <address type='virtio-serial' controller='0' bus='0' port='2'/>
            </channel>
            <input type='tablet' bus='usb'>
                <alias name='input0'/>
                <address type='usb' bus='0' port='1'/>
            </input>
            <input type='mouse' bus='ps2'>
                <alias name='input1'/>
            </input>
            <input type='keyboard' bus='ps2'>
                <alias name='input2'/>
            </input>
            <graphics type='spice' port='5901' autoport='yes' listen='127.0.0.1'>
                <listen type='address' address='127.0.0.1'/>
                <image compression='off'/>
            </graphics>
            <sound model='ich9'>
                <alias name='sound0'/>
                <address type='pci' domain='0x0000' bus='0x00' slot='0x1b' function='0x0'/>
            </sound>
            <audio id='1' type='spice'/>
            <video>
                <model type='virtio' heads='1' primary='yes'/>
                <alias name='video0'/>
                <address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x0'/>
            </video>
            <redirdev bus='usb' type='spicevmc'>
                <alias name='redir0'/>
                <address type='usb' bus='0' port='2'/>
            </redirdev>
            <redirdev bus='usb' type='spicevmc'>
                <alias name='redir1'/>
                <address type='usb' bus='0' port='3'/>
            </redirdev>
            <memballoon model='virtio'>
                <alias name='balloon0'/>
                <address type='pci' domain='0x0000' bus='0x05' slot='0x00' function='0x0'/>
            </memballoon>
            <rng model='virtio'>
                <backend model='random'>/dev/urandom</backend>
                <alias name='rng0'/>
                <address type='pci' domain='0x0000' bus='0x06' slot='0x00' function='0x0'/>
            </rng>
        </devices>
        <seclabel type='dynamic' model='apparmor' relabel='yes'>
            <label>libvirt-{uuid.uuid4()}</label>
            <imagelabel>libvirt-{uuid.uuid4()}</imagelabel>
        </seclabel>
        <seclabel type='dynamic' model='dac' relabel='yes'>
            <label>+64055:+109</label>
            <imagelabel>+64055:+109</imagelabel>
        </seclabel>
    </domain>
    """

def create_vm_in_background(vm_name, config_xml):
    conn = connect_libvirt()
    try:
        dom = conn.defineXML(config_xml)  # Define the VM in libvirt
        dom.create()  # Start the VM
        print(f'VM {vm_name} created successfully')
        subprocess.Popen(['virt-viewer', vm_name])
        conn.close()
    except libvirt.libvirtError as e:
        print(f'Failed to create VM {vm_name}: {str(e)}')
        conn.close()

@app.route('/vms', methods=['POST'])
def create_vm():
    vm_data = request.json
    vm_name = vm_data.get('name', f'vm-{uuid.uuid4()}')
    iso_url = vm_data.get('iso_url')
    disk_size_gb = vm_data.get('disk_size_gb', 30)
    memory_mb = vm_data.get('memory_mb', 4096)
    vcpu_count = vm_data.get('vcpu_count', 2)
    disk_path = f'/var/lib/libvirt/images/{vm_name}.qcow2'
    iso_path = f'/var/lib/libvirt/images/{os.path.basename(iso_url)}'

    # Ensure ISO exists
    if not ensure_iso_exists(iso_url, iso_path):
        return 'Failed to download ISO', 500

    # Create a new disk image
    create_disk_image(disk_path, disk_size_gb)  # Create a disk image of the specified size

    # Generate VM XML configuration
    config_xml = generate_vm_xml(vm_name, disk_path, iso_path, memory_mb, vcpu_count)

    # Run VM creation in a background thread
    threading.Thread(target=create_vm_in_background, args=(vm_name, config_xml)).start()

    return 'VM creation started', 202

@app.route('/vms/<vm_name>/modify', methods=['POST'])
def modify_vm(vm_name):
    new_config = request.json
    conn = connect_libvirt()
    try:
        domain = conn.lookupByName(vm_name)
    except libvirt.libvirtError:
        conn.close()
        return 'VM not found', 404

    if domain.isActive():
        return 'VM must be stopped before modification', 400

    current_xml = domain.XMLDesc(0)

    memory_mb = new_config.get('memory_mb')
    vcpu_count = new_config.get('vcpu_count')

    if memory_mb:
        new_memory_element = f"<memory unit='KiB'>{memory_mb * 1024}</memory>"
        current_xml = current_xml.replace(
            f"<memory unit='KiB'>{domain.maxMemory()}</memory>", 
            new_memory_element
        )

    if vcpu_count:
        new_vcpu_element = f"<vcpu placement='static'>{vcpu_count}</vcpu>"
        current_xml = current_xml.replace(
            f"<vcpu placement='static'>{domain.maxVcpus()}</vcpu>", 
            new_vcpu_element
        )

    try:
        domain.undefine()
        conn.defineXML(current_xml)
        conn.close()
        return 'VM modified successfully', 200
    except libvirt.libvirtError as e:
        conn.close()
        return f'Failed to modify VM configuration: {str(e)}', 400

#-------------------------------------------------
# UnMount ISO
@app.route('/vms/<vm_name>/unmount_iso', methods=['POST'])
def unmount_iso(vm_name):
    conn = connect_libvirt()
    try:
        domain = conn.lookupByName(vm_name)
    except libvirt.libvirtError:
        conn.close()
        return 'VM not found', 404

    current_xml = domain.XMLDesc(0)
    disk_section_start = current_xml.find("<disk type='file' device='cdrom'>")
    disk_section_end = current_xml.find("</disk>", disk_section_start) + len("</disk>")

    if disk_section_start != -1 and disk_section_end != -1:
        new_xml = current_xml[:disk_section_start] + current_xml[disk_section_end:]
    else:
        conn.close()
        return 'No CDROM device found', 400

    try:
        domain.undefine()
        conn.defineXML(new_xml)
        conn.close()
        return 'ISO unmounted and VM configuration updated', 200
    except libvirt.libvirtError as e:
        conn.close()
        return f'Failed to update VM configuration: {str(e)}', 400

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
    try:
        domain = conn.lookupByName(vm_name)
    except libvirt.libvirtError:
        conn.close()
        return 'VM not found', 404

    if domain.isActive():
        domain.destroy()
    domain.undefine()
    conn.close()
    disk_path = f'/var/lib/libvirt/images/{vm_name}.qcow2'
    if os.path.exists(disk_path):
        os.remove(disk_path)
    return 'VM deleted', 204

#-------------------------------------------------
# Start VM
@app.route('/vms/<vm_name>/start', methods=['POST'])
def start_vm(vm_name):
    conn = connect_libvirt()
    try:
        domain = conn.lookupByName(vm_name)
    except libvirt.libvirtError:
        conn.close()
        return 'VM not found', 404

    disk_path = f'/var/lib/libvirt/images/{vm_name}.qcow2'  # Construye la ruta del disco duro correctamente

    if not os.path.exists(disk_path):
        conn.close()
        return 'Disk image not found', 404

    try:
        domain.create()
        conn.close()
        subprocess.Popen(['virt-viewer', vm_name])
        return 'VM started', 200
    except libvirt.libvirtError as e:
        conn.close()
        return f'Failed to start VM: {str(e)}', 400

#-------------------------------------------------
# Stop VM
@app.route('/vms/<vm_name>/stop', methods=['POST'])
def stop_vm(vm_name):
    conn = connect_libvirt()
    try:
        domain = conn.lookupByName(vm_name)
    except libvirt.libvirtError:
        conn.close()
        return 'VM not found', 404

    try:
        domain.destroy()
        while domain.isActive():
            pass  # Espera hasta que la VM se apague
        conn.close()
        return 'VM stopped', 200
    except libvirt.libvirtError as e:
        conn.close()
        return f'Failed to stop VM: {str(e)}', 400


#-------------------------------------------------
# Export VM
@app.route('/vms/<vm_name>/export', methods=['GET'])
def export_vm(vm_name):
    conn = connect_libvirt()
    try:
        domain = conn.lookupByName(vm_name)
    except libvirt.libvirtError:
        conn.close()
        return 'VM not found', 404

    if domain.isActive():
        return 'VM must be stopped before export', 400

    xml_desc = domain.XMLDesc(0)
    disk_path = f'/var/lib/libvirt/images/{vm_name}.qcow2'
    if not os.path.exists(disk_path):
        conn.close()
        return 'Disk image not found', 404

    # Determine the user's desktop directory
    home_dir = Path.home()
    desktop_dir = home_dir / 'Desktop'
    if not desktop_dir.exists():
        desktop_dir = home_dir / 'Escritorio'
        if not desktop_dir.exists():
            conn.close()
            return 'Desktop directory not found', 404

    # Create temporary files on the desktop
    xml_file_path = desktop_dir / f'{vm_name}.xml'
    with open(xml_file_path, 'w') as xml_file:
        xml_file.write(xml_desc)

    # Create a tar archive containing both the XML and QCOW2 files
    tar_path = desktop_dir / f'{vm_name}.tar'
    with tarfile.open(tar_path, 'w') as tar:
        tar.add(xml_file_path, arcname=f'{vm_name}.xml')
        tar.add(disk_path, arcname=f'{vm_name}.qcow2')

    # Clean up temporary files
    os.remove(xml_file_path)

    conn.close()
    return f'VM exported to {tar_path}', 200


#-------------------------------------------------
# Export VM Compressed tar.gz
@app.route('/vms/<vm_name>/exportCompressed', methods=['GET'])
def exportCompressed_vm(vm_name):
    conn = connect_libvirt()
    try:
        domain = conn.lookupByName(vm_name)
    except libvirt.libvirtError:
        conn.close()
        return 'VM not found', 404

    if domain.isActive():
        return 'VM must be stopped before export', 400

    xml_desc = domain.XMLDesc(0)
    disk_path = f'/var/lib/libvirt/images/{vm_name}.qcow2'
    if not os.path.exists(disk_path):
        conn.close()
        return 'Disk image not found', 404

    # Determine the user's desktop directory
    home_dir = Path.home()
    desktop_dir = home_dir / 'Desktop'
    if not desktop_dir.exists():
        desktop_dir = home_dir / 'Escritorio'
        if not desktop_dir.exists():
            conn.close()
            return 'Desktop directory not found', 404

    # Create temporary files on the desktop
    xml_file_path = desktop_dir / f'{vm_name}.xml'
    with open(xml_file_path, 'w') as xml_file:
        xml_file.write(xml_desc)

    # Create a tar.gz archive containing both the XML and QCOW2 files
    tar_path = desktop_dir / f'{vm_name}.tar.gz'
    with tarfile.open(tar_path, 'w:gz') as tar:
        tar.add(xml_file_path, arcname=f'{vm_name}.xml')
        tar.add(disk_path, arcname=f'{vm_name}.qcow2')

    # Clean up temporary files
    os.remove(xml_file_path)

    conn.close()
    return f'VM exported to {tar_path}', 200

#-------------------------------------------------
#-------------------------------------------------
# Import VM
@app.route('/vms/import', methods=['POST'])
def import_vm():
    conn = connect_libvirt()
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    home_dir = Path.home()
    desktop_dir = home_dir / 'Desktop'
    if not desktop_dir.exists():
        desktop_dir = home_dir / 'Escritorio'
        if not desktop_dir.exists():
            conn.close()
            return 'Desktop directory not found', 404

    # Save the uploaded tar file to a temporary location
    temp_tar_path = desktop_dir / file.filename
    file.save(temp_tar_path)

    # Extract the tar file
    extracted_files = []
    try:
        with tarfile.open(temp_tar_path, 'r') as tar:
            tar.extractall(path=desktop_dir)
            extracted_files = tar.getnames()  # Get list of extracted file names
    except tarfile.TarError as e:
        os.remove(temp_tar_path)
        conn.close()
        return f'Failed to extract tar file: {str(e)}', 500

    # Locate the XML and QCOW2 files
    xml_file_path = None
    qcow2_file_path = None
    for file_name in extracted_files:
        if file_name.endswith('.xml'):
            xml_file_path = desktop_dir / file_name
        elif file_name.endswith('.qcow2'):
            qcow2_file_path = desktop_dir / file_name

    if not xml_file_path or not qcow2_file_path:
        os.remove(temp_tar_path)
        conn.close()
        return 'Invalid tar file contents', 400

    # Read the XML file
    with open(xml_file_path, 'r') as xml_file:
        xml_desc = xml_file.read()

    # Define the new VM using the XML description
    try:
        domain = conn.defineXML(xml_desc)
    except libvirt.libvirtError as e:
        os.remove(temp_tar_path)
        os.remove(xml_file_path)
        os.remove(qcow2_file_path)
        conn.close()
        return f'Failed to define VM: {str(e)}', 500

    # Move the QCOW2 file to the appropriate location
    vm_name = domain.name()
    dest_qcow2_path = Path(f'/var/lib/libvirt/images/{vm_name}.qcow2')
    os.rename(qcow2_file_path, dest_qcow2_path)

    # Update the XML to reference the new disk location
    domain.undefine()  # Undefine the VM temporarily to update the XML
    updated_xml_desc = xml_desc.replace(str(qcow2_file_path), str(dest_qcow2_path))
    try:
        domain = conn.defineXML(updated_xml_desc)
    except libvirt.libvirtError as e:
        os.remove(temp_tar_path)
        os.remove(xml_file_path)
        os.remove(dest_qcow2_path)
        conn.close()
        return f'Failed to redefine VM: {str(e)}', 500

    # Clean up temporary files
    # os.remove(temp_tar_path) # activate this line if you want to remove the tar file after import
    os.remove(xml_file_path)

    conn.close()
    return f'VM {vm_name} imported successfully', 200



#-------------------------------------------------
# Import VM Compressed tar.gz
@app.route('/vms/importCompressed', methods=['POST'])
def importCompressed_vm():
    conn = connect_libvirt()
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    home_dir = Path.home()
    desktop_dir = home_dir / 'Desktop'
    if not desktop_dir.exists():
        desktop_dir = home_dir / 'Escritorio'
        if not desktop_dir.exists():
            conn.close()
            return 'Desktop directory not found', 404

    # Save the uploaded tar.gz file to a temporary location
    temp_tar_path = desktop_dir / file.filename
    file.save(temp_tar_path)

    # Extract the tar.gz file
    extracted_files = []
    try:
        with tarfile.open(temp_tar_path, 'r:gz') as tar:
            tar.extractall(path=desktop_dir)
            extracted_files = tar.getnames()  # Get list of extracted file names
    except tarfile.TarError as e:
        os.remove(temp_tar_path)
        conn.close()
        return f'Failed to extract tar.gz file: {str(e)}', 500

    # Locate the XML and QCOW2 files
    xml_file_path = None
    qcow2_file_path = None
    for file_name in extracted_files:
        if file_name.endswith('.xml'):
            xml_file_path = desktop_dir / file_name
        elif file_name.endswith('.qcow2'):
            qcow2_file_path = desktop_dir / file_name

    if not xml_file_path or not qcow2_file_path:
        os.remove(temp_tar_path)
        conn.close()
        return 'Invalid tar.gz file contents', 400

    # Read the XML file
    with open(xml_file_path, 'r') as xml_file:
        xml_desc = xml_file.read()

    # Define the new VM using the XML description
    try:
        domain = conn.defineXML(xml_desc)
    except libvirt.libvirtError as e:
        os.remove(temp_tar_path)
        os.remove(xml_file_path)
        os.remove(qcow2_file_path)
        conn.close()
        return f'Failed to define VM: {str(e)}', 500

    # Move the QCOW2 file to the appropriate location
    vm_name = domain.name()
    dest_qcow2_path = Path(f'/var/lib/libvirt/images/{vm_name}.qcow2')
    os.rename(qcow2_file_path, dest_qcow2_path)

    # Update the XML to reference the new disk location
    domain.undefine()  # Undefine the VM temporarily to update the XML
    updated_xml_desc = xml_desc.replace(str(qcow2_file_path), str(dest_qcow2_path))
    try:
        domain = conn.defineXML(updated_xml_desc)
    except libvirt.libvirtError as e:
        os.remove(temp_tar_path)
        os.remove(xml_file_path)
        os.remove(dest_qcow2_path)
        conn.close()
        return f'Failed to redefine VM: {str(e)}', 500

    # Clean up temporary files
    # os.remove(temp_tar_path) # Optional: remove this line if you want to keep the tar.gz file
    os.remove(xml_file_path)

    conn.close()
    return f'VM {vm_name} imported successfully', 200

if __name__ == '__main__':
    app.run(debug=True)