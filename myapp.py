from prometheus_client import Gauge, generate_latest
from flask import Flask, request, Response
from pysnmp.hlapi import *
from asgiref.wsgi import WsgiToAsgi
from pysnmp.smi.rfc1902 import ObjectIdentity, ObjectType

app = Flask(__name__)

CONTENT_TYPE_LATEST = str('text/plain; version=0.0.4; charset=utf-8')


@app.route('/')
def hello_world():
    return 'Hello, World!'


prometheus_metric_cpu = Gauge('Trassir_cpu_usage', 'Trassir_cpu_usage', labelnames=['Trassir_cpu_usage'])
prometheus_metric_cameras = Gauge('Trassir_cameras', 'Trassir_cameras', labelnames=['Trassir_cameras'])
prometheus_metric_max_cameras = Gauge('Trassir_max_cameras', 'Trassir_max_cameras',
                                      labelnames=['Trassir_max_cameras'])
prometheus_metric_days = Gauge('Trassir_Archive_days', 'Trassir_Archive_days',
                               labelnames=['Trassir_Archive_days'])
prometheus_metric_db = Gauge('Trassir_db_ok', 'Trassir_db_ok', labelnames=['Trassir_db_ok'])
prometheus_metric_disks = Gauge('Trassir_disks_ok', 'Trassir_disks_ok',
                                labelnames=['Trassir_disks_ok'])


@app.route('/metrics', methods=['GET'])
def metrics():
    prometheus_metric_cpu.clear()
    prometheus_metric_cameras.clear()
    prometheus_metric_max_cameras.clear()
    prometheus_metric_days.clear()
    prometheus_metric_db.clear()
    prometheus_metric_disks.clear()

    target = request.args.get('target')

    oid_list = [
        '1.3.6.1.4.1.3333.1.1',
        '1.3.6.1.4.1.3333.1.2',
        '1.3.6.1.4.1.3333.1.3',
        '1.3.6.1.4.1.3333.1.5',
        '1.3.6.1.4.1.3333.1.8',
    ]

    snmp_response = []

    for oid in oid_list:
        oid_response = {'oid': oid, 'response': snmp_get_next(target, oid)}
        snmp_response.append(oid_response)

    for el in snmp_response:
        if el['response'] is None:
            continue
        if el['oid'] == '1.3.6.1.4.1.3333.1.1':
            prometheus_metric_db.labels(el['response']).set(1)
        if el['oid'] == '1.3.6.1.4.1.3333.1.2':
            prometheus_metric_days.labels(el['response'].split(' / ')[0]).set(1)
        if el['oid'] == '1.3.6.1.4.1.3333.1.3':
            prometheus_metric_disks.labels(el['response']).set(1)
        if el['oid'] == '1.3.6.1.4.1.3333.1.5':
            prometheus_metric_cameras.labels(el['response'].split(' / ')[0]).set(1)
            prometheus_metric_max_cameras.labels(el['response'].split(' / ')[1]).set(1)
        if el['oid'] == '1.3.6.1.4.1.3333.1.8':
            prometheus_metric_cpu.labels(el['response'].split('%')[0]).set(1)

    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


def walk(host, oid):
    return (getCmd(SnmpEngine(),
                   CommunityData('dssl'),
                   UdpTransportTarget((host, '161')),
                   ContextData(),
                   ObjectType(ObjectIdentity(oid))))


def snmp_get_next(host, oid):
    errorIndication, errorStatus, errorIndex, varBinds = next(walk(host, oid))
    for name, val in varBinds:
        return val.prettyPrint()


asgi_app = WsgiToAsgi(app)
# app.run(debug=True)
