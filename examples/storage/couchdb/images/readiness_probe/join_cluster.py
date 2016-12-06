#!/usr/bin/env python
"""
    Usage:  join_cluster.py dbname dbname ...
"""
from subprocess import check_output, CalledProcessError
import requests
import logging
import socket
import json
import sys
import os


def main(system_dbs):
    pod_hostnames = discover_pod_fq_hostnames()
    logging.warning('Using the discovered host names: {0}'.format(pod_hostnames))

    cluster_admin = (os.environ['CLUSTER_ADM_USER'].rstrip(), os.environ['CLUSTER_ADM_PASS'].rstrip())
    populate_nodes_db(pod_hostnames, cluster_admin)
    create_system_dbs(cluster_admin, system_dbs)
    sys.exit(0)


def discover_pod_fq_hostnames():
    hostnames = []
    nslookup_cmd = ["nslookup", "-type=srv"]
    fq_pod_hostname = socket.getfqdn(os.environ['POD_IP'])
    cluster_host = "{}.{}".format(fq_pod_hostname.split('.')[1],
                                  fq_pod_hostname.split('.')[2])
    nslookup_cmd.append(cluster_host)
    nslookup = ""
    try:
        nslookup = check_output(nslookup_cmd)
    except CalledProcessError as e:
        logging.error(e)
        logging.warning('nslookup could not find other nodes.')
    for i in nslookup.split():
        if len(i.split('.')) == 7:
            hostname = i[:-1]
            if hostname not in hostnames:
                hostnames.append(hostname)
    return hostnames


def populate_nodes_db(pod_hostnames, cluster_admin):
    s = requests.Session()
    s.auth = cluster_admin
    node_db_url = "http://localhost:5986/_nodes"
    existing_hostnames = []
    node_docs = ''
    try:
        node_docs = s.get("{0}/_all_docs".format(node_db_url))
        for node_doc in node_docs.json()['rows']:
            existing_hostnames.append(node_doc['id'])

        for pod_hostname in pod_hostnames:
            node_doc = "db@{0}".format(pod_hostname)
            if node_doc not in existing_hostnames:
                r = s.put("{0}/db%40{1}".format(node_db_url, pod_hostname),
                          data='{}')
                return r
    except requests.ConnectionError as e:
        logging.warning(e)
        logging.warning('Could not populated the nodes db over localhost')
        return 1
    return 0


def create_system_dbs(cluster_admin, system_dbs):
    root_url = "http://{0}:5984/{1}"
    s = requests.Session()
    s.auth = cluster_admin

    system_dbs.pop(0)
    try:
        for system_db in system_dbs:
            response = s.get(root_url.format(os.environ['POD_IP'], system_db))
            if response.status_code == 200:
                logging.warning("I have the {0} db".format(system_db))
            else:
                s.put(root_url.format(os.environ['POD_IP'], system_db))
    except requests.ConnectionError as e:
        logging.warning(e)
        logging.warning('Could not connect to host {} for creating system dbs'.format(socket.getfqdn(os.environ['POD_IP'])))
        return 1
    return 0


if __name__ == '__main__':
    system_dbs = sys.argv
    main(system_dbs)
