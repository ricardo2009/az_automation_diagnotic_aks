import json
from flask import Flask, jsonify
from kubernetes import client, config
from collections import OrderedDict

app = Flask(__name__)

# Variável global para armazenar a saída
output_data = {}

# Configurar acesso ao Kubernetes
config.load_kube_config()

# Instanciar clientes API
v1 = client.CoreV1Api()
apps_v1 = client.AppsV1Api()
batch_v1 = client.BatchV1Api()
networking_v1 = client.NetworkingV1Api()
autoscaling_v1 = client.AutoscalingV1Api()

@app.route('/api/pods', methods=['GET'])
def get_pods():
    pods = v1.list_pod_for_all_namespaces(watch=False)
    pod_list = []
    for pod in pods.items:
        pod_info = OrderedDict([
            ('Pod Name', pod.metadata.name),
            ('Namespace', pod.metadata.namespace),
            ('Status', pod.status.phase),
            ('Node', pod.spec.node_name),
            ('Containers', [
            {
                'Container Name': container.name,
                'Image': container.image,
                'Ready': container.ready,
                'Restart Count': container.restart_count
            } for container in (pod.status.container_statuses or [])
            ]),
            ('Labels', pod.metadata.labels),
            ('Annotations', pod.metadata.annotations),
            ('Creation Timestamp', pod.metadata.creation_timestamp),
            ('IP', pod.status.pod_ip),
            ('Host IP', pod.status.host_ip),
            ('QoS Class', pod.status.qos_class),
            ('Node Selector', pod.spec.node_selector),
            ('Tolerations', [{'Key': toleration.key, 'Operator': toleration.operator, 'Value': toleration.value, 'Effect': toleration.effect} for toleration in (pod.spec.tolerations or [])]),
            ('Affinity', pod.spec.affinity.to_dict() if pod.spec.affinity else None),
            ('Volumes', [{'Name': volume.name, 'Type': type(volume).__name__} for volume in (pod.spec.volumes or [])]),
            ('Conditions', [{'Type': condition.type, 'Status': condition.status, 'Reason': condition.reason, 'Message': condition.message} for condition in (pod.status.conditions or [])]),
            ('Host Aliases', [{'IP': alias.ip, 'Hostnames': alias.hostnames} for alias in (pod.spec.host_aliases or [])]),
            ('Host Network', pod.spec.host_network),
            ('Host PID', pod.spec.host_pid),
            ('Host IPC', pod.spec.host_ipc),
            ('Security Context', pod.spec.security_context.to_dict() if pod.spec.security_context else None),
            ('Image Pull Secrets', [{'Name': secret.name} for secret in (pod.spec.image_pull_secrets or [])]),
            ('Service Account Name', pod.spec.service_account_name),
            ('Automount Service Account Token', pod.spec.automount_service_account_token),
            ('Priority', pod.spec.priority),
            ('Priority Class Name', pod.spec.priority_class_name),
            ('DNS Policy', pod.spec.dns_policy),
            ('DNS Config', pod.spec.dns_config.to_dict() if pod.spec.dns_config else None),
            ('Scheduler Name', pod.spec.scheduler_name),
            ('Init Containers', [
            {
                'Container Name': container.name,
                'Image': container.image,
                'Ready': container.ready,
                'Restart Count': container.restart_count
            } for container in (pod.status.init_container_statuses or [])
            ]),
            ('Ephemeral Containers', [
            {
                'Container Name': container.name,
                'Image': container.image,
                'Ready': container.ready,
                'Restart Count': container.restart_count
            } for container in (pod.status.ephemeral_container_statuses or [])
            ]),
            ('Overhead', pod.spec.overhead),
            ('Runtime Class Name', pod.spec.runtime_class_name),
            ('Topology Spread Constraints', [constraint.to_dict() for constraint in (pod.spec.topology_spread_constraints or [])]),
            ('Affinity', pod.spec.affinity.to_dict() if pod.spec.affinity else None),
            ('Priority', pod.spec.priority),
            ('Priority Class Name', pod.spec.priority_class_name),
            ('DNS Policy', pod.spec.dns_policy),
            ('DNS Config', pod.spec.dns_config.to_dict() if pod.spec.dns_config else None),
            ('Scheduler Name', pod.spec.scheduler_name)
        ])
        pod_list.append(pod_info)
    return jsonify(pod_list)
    nodes = v1.list_node()
    node_list = []
    for node in nodes.items:
        node_info = OrderedDict([
            ('Name', node.metadata.name),
            ('Status', node.status.conditions[-1].type if node.status.conditions else None),
            ('Addresses', [{'Type': addr.type, 'Address': addr.address} for addr in (node.status.addresses or [])]),
            ('Capacity', node.status.capacity),
            ('Allocatable', node.status.allocatable),
            ('OS Image', node.status.node_info.os_image),
            ('Kernel Version', node.status.node_info.kernel_version),
            ('Container Runtime Version', node.status.node_info.container_runtime_version),
            ('Kubelet Version', node.status.node_info.kubelet_version),
            ('Kube-Proxy Version', node.status.node_info.kube_proxy_version),
            ('Architecture', node.status.node_info.architecture),
            ('Operating System', node.status.node_info.operating_system),
            ('Pod CIDR', node.spec.pod_cidr),
            ('Provider ID', node.spec.provider_id),
            ('Taints', [{'Key': taint.key, 'Effect': taint.effect, 'Value': taint.value} for taint in (node.spec.taints or [])]),
            ('Conditions', [{'Type': condition.type, 'Status': condition.status, 'Reason': condition.reason, 'Message': condition.message} for condition in (node.status.conditions or [])]),
            ('Labels', node.metadata.labels),
            ('Annotations', node.metadata.annotations),
            ('Creation Timestamp', node.metadata.creation_timestamp),
            ('Kubelet Port', node.status.daemon_endpoints.kubelet_endpoint.port if node.status.daemon_endpoints.kubelet_endpoint else None),
            ('System UUID', node.status.node_info.system_uuid),
            ('daemonEndpoints', node.status.daemon_endpoints.to_dict() if node.status.daemon_endpoints else None),
            ('Images', [{'Names': image.names, 'SizeBytes': image.size_bytes} for image in (node.status.images or [])]),
            ('Info', node.status.node_info.to_dict() if node.status.node_info else None),
            ('Capacity', node.status.capacity),
            ('Unschedulable', node.spec.unschedulable),
        ])
        node_list.append(node_info)
    
    # Armazenar a saída na variável global
    output_data['nodes'] = node_list
    return jsonify(node_list)

@app.route('/api/deployments', methods=['GET'])
def get_deployments():
    deployments = apps_v1.list_deployment_for_all_namespaces(watch=False)
    deployment_list = []
    for deployment in deployments.items:
        deployment_info = OrderedDict([
            ('Name', deployment.metadata.name),
            ('Namespace', deployment.metadata.namespace),
            ('Replicas', deployment.spec.replicas),
            ('Available Replicas', deployment.status.available_replicas),
            ('Unavailable Replicas', deployment.status.unavailable_replicas),
            ('Labels', deployment.metadata.labels),
            ('Annotations', deployment.metadata.annotations),
            ('Creation Timestamp', deployment.metadata.creation_timestamp),
            ('Strategy', deployment.spec.strategy.to_dict() if deployment.spec.strategy else None),
            ('Min Ready Seconds', deployment.spec.min_ready_seconds),
            ('Revision History Limit', deployment.spec.revision_history_limit),
            ('Progress Deadline Seconds', deployment.spec.progress_deadline_seconds),
            ('Replicas', deployment.status.replicas),
            ('Updated Replicas', deployment.status.updated_replicas),
            ('Ready Replicas', deployment.status.ready_replicas),
            ('Conditions', [{'Type': condition.type, 'Status': condition.status, 'Reason': condition.reason, 'Message': condition.message} for condition in (deployment.status.conditions or [])]),
            ('Selector', deployment.spec.selector.match_labels),
            ('Template', deployment.spec.template.to_dict() if deployment.spec.template else None),
            ('Strategy', deployment.spec.strategy.to_dict() if deployment.spec.strategy else None),
            ('Status', deployment.status.to_dict() if deployment.status else None),
            ('Progress Deadline Seconds', deployment.spec.progress_deadline_seconds),
            ('Min Ready Seconds', deployment.spec.min_ready_seconds),
            ('Revision History Limit', deployment.spec.revision_history_limit),
            ('Paused', deployment.spec.paused),
            ('Rollback To', deployment.spec.rollback_to.to_dict() if deployment.spec.rollback_to else None),
            ('Progress Deadline Seconds', deployment.spec.progress_deadline_seconds),
            ('Min Ready Seconds', deployment.spec.min_ready_seconds),
            ('Revision History Limit', deployment.spec.revision_history_limit)
        ])
        deployment_list.append(deployment_info)
    return jsonify(deployment_list)

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    jobs = batch_v1.list_job_for_all_namespaces(watch=False)
    job_list = []
    for job in jobs.items:
        job_info = OrderedDict([
            ('Name', job.metadata.name),
            ('Namespace', job.metadata.namespace),
            ('Completions', job.spec.completions),
            ('Parallelism', job.spec.parallelism),
            ('Active', job.status.active),
            ('Succeeded', job.status.succeeded),
            ('Failed', job.status.failed),
            ('Labels', job.metadata.labels),
            ('Annotations', job.metadata.annotations),
            ('Creation Timestamp', job.metadata.creation_timestamp),
            ('Conditions', [{'Type': condition.type, 'Status': condition.status, 'Reason': condition.reason, 'Message': condition.message} for condition in (job.status.conditions or [])]),
            ('Selector', job.spec.selector.match_labels),
            ('Template', job.spec.template.to_dict() if job.spec.template else None),
            ('Backoff Limit', job.spec.backoff_limit),
            ('Active Deadline Seconds', job.spec.active_deadline_seconds),
            ('Completion Mode', job.spec.completion_mode),
            ('Manual Selector', job.spec.manual_selector),
            ('Parallelism', job.spec.parallelism),
            ('TTL Seconds After Finished', job.spec.ttl_seconds_after_finished),
            ('Parallelism', job.spec.parallelism),
            ('TTL Seconds After Finished', job.spec.ttl_seconds_after_finished),
            ('Parallelism', job.spec.parallelism),
            ('TTL Seconds After Finished', job.spec.ttl_seconds_after_finished)
        ])
        job_list.append(job_info)
    return jsonify(job_list)

@app.route('/api/services', methods=['GET'])
def get_services():
    services = v1.list_service_for_all_namespaces(watch=False)
    service_list = []
    for service in services.items:
        service_info = OrderedDict([
            ('Name', service.metadata.name),
            ('Namespace', service.metadata.namespace),
            ('Type', service.spec.type),
            ('Cluster IP', service.spec.cluster_ip),
            ('External IPs', service.spec.external_i_ps),
            ('Ports', [{'Name': port.name, 'Protocol': port.protocol, 'Port': port.port, 'Target Port': port.target_port, 'Node Port': port.node_port} for port in (service.spec.ports or [])]),
            ('Selector', service.spec.selector),
            ('Load Balancer IP', service.status.load_balancer.ingress[0].ip if service.status.load_balancer.ingress else None),
            ('Load Balancer Hostname', service.status.load_balancer.ingress[0].hostname if service.status.load_balancer.ingress else None),
            ('Load Balancer Ingress', [{'IP': ingress.ip, 'Hostname': ingress.hostname} for ingress in (service.status.load_balancer.ingress or [])]),
            ('External Name', service.spec.external_name),
            ('External Traffic Policy', service.spec.external_traffic_policy),
            ('Session Affinity', service.spec.session_affinity),
            ('Session Affinity Config', service.spec.session_affinity_config.to_dict() if service.spec.session_affinity_config else None),
            ('IP Family Policy', service.spec.ip_family_policy),
            ('Topology Keys', service.spec.topology_keys),
            ('Publish Not Ready Addresses', service.spec.publish_not_ready_addresses),
            ('Health Check Node Port', service.spec.health_check_node_port),
            ('Session Affinity', service.spec.session_affinity),
            ('Session Affinity Config', service.spec.session_affinity_config.to_dict() if service.spec.session_affinity_config else None),
            ('IP Family Policy', service.spec.ip_family_policy),
            ('Topology Keys', service.spec.topology_keys),
            ('Publish Not Ready Addresses', service.spec.publish_not_ready_addresses),
            ('Health Check Node Port', service.spec.health_check_node_port),
            ('Session Affinity', service.spec.session_affinity),
            ('Session Affinity Config', service.spec.session_affinity_config.to_dict() if service.spec.session_affinity_config else None),
            ('IP Family Policy', service.spec.ip_family_policy),
            ('Topology Keys', service.spec.topology_keys),
            ('Publish Not Ready Addresses', service.spec.publish_not_ready_addresses),
            ('Health Check Node Port', service.spec.health_check_node_port)
        ])
        service_list.append(service_info)
    return jsonify(service_list)

@app.route('/api/ingresses', methods=['GET'])
def get_ingresses():
    ingresses = networking_v1.list_ingress_for_all_namespaces(watch=False)
    ingress_list = []
    for ingress in ingresses.items:
        ingress_info = OrderedDict([
            ('Name', ingress.metadata.name),
            ('Namespace', ingress.metadata.namespace),
            ('Hosts', ingress.spec.rules[0].host if ingress.spec.rules else None),
            ('Paths', [{'Path': rule.http.paths[0].path, 'Backend': rule.http.paths[0].backend.service_name} for rule in (ingress.spec.rules or [])]),
            ('TLS', [{'Hosts': tls.hosts, 'Secret Name': tls.secret_name} for tls in (ingress.spec.tls or [])]),
            ('Backend', ingress.spec.default_backend.service_name if ingress.spec.default_backend else None),
            ('Labels', ingress.metadata.labels),
            ('Annotations', ingress.metadata.annotations),
            ('Creation Timestamp', ingress.metadata.creation_timestamp),
            ('Conditions', [{'Type': condition.type, 'Status': condition.status, 'Reason': condition.reason, 'Message': condition.message} for condition in (ingress.status.conditions or [])]),
            ('Backend', ingress.spec.default_backend.service_name if ingress.spec.default_backend else None),
            ('TLS', [{'Hosts': tls.hosts, 'Secret Name': tls.secret_name} for tls in (ingress.spec.tls or [])]),
            ('Backend', ingress.spec.default_backend.service_name if ingress.spec.default_backend else None),
            ('Labels', ingress.metadata.labels),
            ('Annotations', ingress.metadata.annotations),
            ('Creation Timestamp', ingress.metadata.creation_timestamp),
            ('Conditions', [{'Type': condition.type, 'Status': condition.status, 'Reason': condition.reason, 'Message': condition.message} for condition in (ingress.status.conditions or [])]),
            ('Backend', ingress.spec.default_backend.service_name if ingress.spec.default_backend else None),
            ('TLS', [{'Hosts': tls.hosts, 'Secret Name': tls.secret_name} for tls in (ingress.spec.tls or [])]),
            ('Backend', ingress.spec.default_backend.service_name if ingress.spec.default_backend else None),
            ('Labels', ingress.metadata.labels),
            ('Annotations', ingress.metadata.annotations),
            ('Creation Timestamp', ingress.metadata.creation_timestamp),
            ('Conditions', [{'Type': condition.type, 'Status': condition.status, 'Reason': condition.reason, 'Message': condition.message} for condition in (ingress.status.conditions or [])])
        ])
        ingress_list.append(ingress_info)
    return jsonify(ingress_list)

@app.route('/api/horizontalpodautoscalers', methods=['GET'])
def get_horizontalpodautoscalers():
    horizontalpodautoscalers = autoscaling_v1.list_horizontal_pod_autoscaler_for_all_namespaces(watch=False)
    horizontalpodautoscaler_list = []
    for horizontalpodautoscaler in horizontalpodautoscalers.items:
        horizontalpodautoscaler_info = OrderedDict([
            ('Name', horizontalpodautoscaler.metadata.name),
            ('Namespace', horizontalpodautoscaler.metadata.namespace),
            ('Min Replicas', horizontalpodautoscaler.spec.min_replicas),
            ('Max Replicas', horizontalpodautoscaler.spec.max_replicas),
            ('Current Replicas', horizontalpodautoscaler.status.current_replicas),
            ('Desired Replicas', horizontalpodautoscaler.status.desired_replicas),
            ('Current Metrics', [{'Type': metric.type, 'Value': metric.value} for metric in (horizontalpodautoscaler.status.current_metrics or [])]),
            ('Target Metrics', [{'Type': metric.type, 'Value': metric.value} for metric in (horizontalpodautoscaler.spec.metrics or [])]),
            ('Labels', horizontalpodautoscaler.metadata.labels),
            ('Annotations', horizontalpodautoscaler.metadata.annotations),
            ('Creation Timestamp', horizontalpodautoscaler.metadata.creation_timestamp),
            ('Conditions', [{'Type': condition.type, 'Status': condition.status, 'Reason': condition.reason, 'Message': condition.message} for condition in (horizontalpodautoscaler.status.conditions or [])]),
            ('Min Replicas', horizontalpodautoscaler.spec.min_replicas),
            ('Max Replicas', horizontalpodautoscaler.spec.max_replicas),
            ('Current Replicas', horizontalpodautoscaler.status.current_replicas),
            ('Desired Replicas', horizontalpodautoscaler.status.desired_replicas),
            ('Current Metrics', [{'Type': metric.type, 'Value': metric.value} for metric in (horizontalpodautoscaler.status.current_metrics or [])]),
            ('Target Metrics', [{'Type': metric.type, 'Value': metric.value} for metric in (horizontalpodautoscaler.spec.metrics or [])]),
            ('Labels', horizontalpodautoscaler.metadata.labels),
            ('Annotations', horizontalpodautoscaler.metadata.annotations),
            ('Creation Timestamp', horizontalpodautoscaler.metadata.creation_timestamp),
            ('Conditions', [{'Type': condition.type, 'Status': condition.status, 'Reason': condition.reason, 'Message': condition.message} for condition in (horizontalpodautoscaler.status.conditions or [])]),
            ('Min Replicas', horizontalpodautoscaler.spec.min_replicas),
            ('Max Replicas', horizontalpodautoscaler.spec.max_replicas),
            ('Current Replicas', horizontalpodautoscaler.status.current_replicas),
            ('Desired Replicas', horizontalpodautoscaler.status.desired_replicas),
            ('Current Metrics', [{'Type': metric.type, 'Value': metric.value} for metric in (horizontalpodautoscaler.status.current_metrics or [])]),
            ('Target Metrics', [{'Type': metric.type, 'Value': metric.value} for metric in (horizontalpodautoscaler.spec.metrics or [])]),
            ('Labels', horizontalpodautoscaler.metadata.labels),
            ('Annotations', horizontalpodautoscaler.metadata.annotations),
            ('Creation Timestamp', horizontalpodautoscaler.metadata.creation_timestamp),
            ('Conditions', [{'Type': condition.type, 'Status': condition.status, 'Reason': condition.reason, 'Message': condition.message} for condition in (horizontalpodautoscaler.status.conditions or [])])
        ])
        horizontalpodautoscaler_list.append(horizontalpodautoscaler_info)
    return jsonify(horizontalpodautoscaler_list)

@app.route('/api/nodes', methods=['GET'])
def get_nodes():
    nodes = v1.list_node()
    node_list = []
    for node in nodes.items:
        node_info = OrderedDict([
            ('Name', node.metadata.name),
            ('Status', node.status.conditions[-1].type if node.status.conditions else None),
            ('Addresses', [{'Type': addr.type, 'Address': addr.address} for addr in (node.status.addresses or [])]),
            ('Capacity', node.status.capacity),
            ('Allocatable', node.status.allocatable),
            ('OS Image', node.status.node_info.os_image),
            ('Kernel Version', node.status.node_info.kernel_version),
            ('Container Runtime Version', node.status.node_info.container_runtime_version),
            ('Kubelet Version', node.status.node_info.kubelet_version),
            ('Kube-Proxy Version', node.status.node_info.kube_proxy_version),
            ('Architecture', node.status.node_info.architecture),
            ('Operating System', node.status.node_info.operating_system),
            ('Pod CIDR', node.spec.pod_cidr),
            ('Provider ID', node.spec.provider_id),
            ('Taints', [{'Key': taint.key, 'Effect': taint.effect, 'Value': taint.value} for taint in (node.spec.taints or [])]),
            ('Conditions', [{'Type': condition.type, 'Status': condition.status, 'Reason': condition.reason, 'Message': condition.message} for condition in (node.status.conditions or [])]),
            ('Labels', node.metadata.labels),
            ('Annotations', node.metadata.annotations),
            ('Creation Timestamp', node.metadata.creation_timestamp),
            ('Kubelet Port', node.status.daemon_endpoints.kubelet_endpoint.port if node.status.daemon_endpoints.kubelet_endpoint else None),
            ('System UUID', node.status.node_info.system_uuid),
            ('daemonEndpoints', node.status.daemon_endpoints.to_dict() if node.status.daemon_endpoints else None),
            ('Images', [{'Names': image.names, 'SizeBytes': image.size_bytes} for image in (node.status.images or [])]),
            ('Info', node.status.node_info.to_dict() if node.status.node_info else None),
            ('Capacity', node.status.capacity),
            ('Unschedulable', node.spec.unschedulable),
        ])
        node_list.append(node_info)
    
    # Armazenar a saída na variável global
    output_data['nodes'] = node_list
    return jsonify(node_list)
            
# Continue modificando as outras rotas da mesma forma...

if __name__ == '__main__':
    app.run(debug=True)


# Para criar um arquivo requirements.txt, execute o seguinte comando:
# pip freeze > requirements.txt 

# Para instalar as dependências, execute o seguinte comando:
#python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
# source venv/bin/activate && pip install -r requirements.txt 

# Para executar o servidor, execute o seguinte comando:
# python k8s.py

# Para acessar a documentação da API, acesse o seguinte link:
