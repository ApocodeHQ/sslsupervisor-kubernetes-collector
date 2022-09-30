#!/usr/bin/env python3

import logging
import time
import requests
import os
from kubernetes import client, config, watch


VERSION = '0.0.1'
SSLSUPERVISOR_CLUSTER_NAME = os.getenv('SSLSUPERVISOR_CLUSTER_NAME')
SSLSUPERVISOR_API_KEY = os.getenv('SSLSUPERVISOR_API_KEY')
WAIT_TIME = 300


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logger.info('Starting...')

    logger.info('Loading Kubernetes Config')

    config.load_incluster_config()

    api_client = client.ApiClient()
    api_instance = client.NetworkingV1Api(api_client)

    while True:
        logger.info('Listing ingresses')
        ingress_response = api_instance.list_ingress_for_all_namespaces()
        
        domains = []
        for ingress in ingress_response.items:
            for rule in ingress.spec.rules:
                domains.append(rule.host)

        logger.info('Listing ingresses done')
        logger.info(domains)

        try:
            r = requests.post(
                'https://sslsupervisor.api.apocode.io/api/v1/identity/integrations/kubernetes/callback',
                json={
                    'kubernetes_cluster_name': os.getenv('SSLSUPERVISOR_CLUSTER_NAME'),
                    'kubernetes_data': domains,
                    'kubernetes_integration_version': VERSION,
                },
                headers = {
                    'X-Apo-Api-Key': os.getenv('SSLSUPERVISOR_API_KEY'),
                }
            )
            logger.info(r.json())
            r.raise_for_status()

            logger.info(f'Done!')

        except Exception as e:
            logger.error(e)
            logger.info(f'Failed. See error above.')


        logger.info(f'Waiting {WAIT_TIME} second before next update...')
        time.sleep(WAIT_TIME)
        
