import networkx as nx
from yafs import Application, Message, Topology


def create_smart_healthcare_application(digital_twin):
    app = Application(name="SmartHealthcare")

    modules = []

    for sensor in digital_twin.sensors:
        client_module = f"Client_Module_Sensor_{sensor.device_id}"
        processing_module = f"Processing_Module_Sensor_{sensor.device_id}"

        modules.append(
            {client_module: {"Type": Application.TYPE_SOURCE, "RAM": 10, "IPT": 1000}}
        )

        modules.append(
            {
                processing_module: {
                    "Type": Application.TYPE_MODULE,
                    "RAM": 50,
                    "IPT": int(sensor.averageFlowSize),
                }
            }
        )

    modules.append(
        {"Storage_Module": {"Type": Application.TYPE_SINK, "RAM": 100, "IPT": 500}}
    )

    app.set_modules(modules)

    for sensor in digital_twin.sensors:
        client_module = f"Client_Module_Sensor_{sensor.device_id}"
        processing_module = f"Processing_Module_Sensor_{sensor.device_id}"
        sensor_msg = f"sensor_msg_{sensor.device_id}"
        result_msg = f"result_msg_{sensor.device_id}"

        msg = Message(
            name=sensor_msg,
            src=client_module,
            dst=processing_module,
            instructions=int(sensor.averageFlowSize),
            bytes=int(sensor.flowTrafficSize * 1000000),
        )
        app.add_source_messages(msg)

        app.add_service_module(processing_module, sensor_msg, message_out=[result_msg])

    result_messages = [
        f"result_msg_{sensor.device_id}" for sensor in digital_twin.sensors
    ]
    app.add_service_module("Storage_Module", result_messages, message_out=[])

    return app


def create_yafs_topology(digital_twin):
    G = nx.Graph()

    edge_node_names = [f"edge_{i}" for i in range(len(digital_twin.edge_nodes))]
    all_nodes = edge_node_names + ["proxy", "cloud"]

    G.add_nodes_from(all_nodes)

    for i in range(len(digital_twin.edge_nodes)):
        G.add_edge(f"edge_{i}", "proxy")

    G.add_edge("proxy", "cloud")

    topology = Topology()
    topology.create_topology_from_graph(G)

    for i, edge_node in enumerate(digital_twin.edge_nodes):
        node_name = f"edge_{i}"
        topology.G.nodes[node_name]["IPT"] = int(edge_node.processingPower)
        topology.G.nodes[node_name]["RAM"] = 1000
        topology.G.nodes[node_name]["STORAGE"] = 10000

    topology.G.nodes["proxy"]["IPT"] = 10000
    topology.G.nodes["proxy"]["RAM"] = 2000
    topology.G.nodes["proxy"]["STORAGE"] = 50000

    if digital_twin.cloud_node is not None:
        cloud = digital_twin.cloud_node
        topology.G.nodes["cloud"]["IPT"] = int(cloud.processingPower)
        topology.G.nodes["cloud"]["RAM"] = 10000
        topology.G.nodes["cloud"]["STORAGE"] = 100000

    for i in range(len(digital_twin.edge_nodes)):
        topology.G.edges[f"edge_{i}", "proxy"]["BW"] = 100
        topology.G.edges[f"edge_{i}", "proxy"]["PR"] = 4

    topology.G.edges["proxy", "cloud"]["BW"] = 1000
    topology.G.edges["proxy", "cloud"]["PR"] = 100

    return topology
