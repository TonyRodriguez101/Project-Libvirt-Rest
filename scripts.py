from flask import Flask, request, jsonify
import libvirt


app = Flask(__name__)

def connect_libvirt():
    return libvirt.open('qemu:///system')

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
    domain.undefine()
    domain.destroy()
    conn.close()
    return 'VM deleted', 204

#-------------------------------------------------
# Start VM

@app.route('/vms/<vm_name>/start', methods=['POST'])
def start_vm(vm_name):
    conn = connect_libvirt()
    domain = conn.lookupByName(vm_name)
    domain.create()
    conn.close()
    return 'VM started', 200


#-------------------------------------------------
# Stop VM
@app.route('/vms/<vm_name>/stop', methods=['POST'])
def stop_vm(vm_name):
    conn = connect_libvirt()
    domain = conn.lookupByName(vm_name)
    domain.shutdown()
    conn.close()
    return 'VM stopped', 200


#-------------------------------------------------
# Create VM
@app.route('/vms', methods=['POST'])
def create_vm():
    config_xml = request.data.decode()
    conn = connect_libvirt()
    conn.createXML(config_xml, 0)
    conn.close()
    return 'VM created', 201


if __name__ == '__main__':
    app.run(debug=True)
