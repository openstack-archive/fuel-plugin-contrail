# # from helpers.client_contrail import client_contrail
#
# import pytest
#
# # from stepler.conftest import *
# # from stepler.conftest import __all__
#
#
#
#
#
#
# @pytest.fixture(scope='class', params=[1, 2, 3, 4])
# def xxx(request):
#     """XXX fixture"""
#     print('$' * 80)
#     print('xxx: %s' % request)
#     print('$' * 80)
#
#
# # @pytest.mark.smoke_test
# # class Test_smoke(object):
# #
# #     # def test_contrail_status(self, logger, client_contrail):
# #     #     # client_contrail.get_networks()
# #     #     logger.error(client_contrail)
# #     #
# #     #
# #     # def test_one(self, logger, xxx, request):
# #     #     logger.debug('[test_one] 1111')
# #     #     print('[test_one] done')
# #
# #
# #     def test_two(self, logger, xxx):
# #         logger.error('[test_two] 2222')
# #         print('[test_two] done')
#
#
# # @pytest.mark.smoke_test
# # def test_contrail(nova_client):
# #     print nova_client
#
#
# from vapor.helpers.clients.contrail_api import ContrailClient
# from vapor.settings import CONTRAIL_CREDS
#
#
# @pytest.yield_fixture
# def client_contrail():
#     print('[client_contrail]')
#     with ContrailClient(CONTRAIL_CREDS['controller_addr']) as contrail:
#         print('[client_contrail] yield')
#         yield contrail
#         print('[client_contrail] yield done')
#     print('helpers.clients.client_contrail')
#
#
# @pytest.mark.idempotent_id('1b1a0953-a772-4cfe-a7da-2f6de950e456')
# def test_contrail_1(client_contrail):
#     print('[test_contrail_1]->')
#     print client_contrail.get_route_tables()
#     print('[test_contrail_1]<-')
#
#
# @pytest.mark.parametrize("contrail_node_role", [
#     'contrail-controller',
#     'contrail-analytics'
#     'contrail-analytics-db'
# ])
# @pytest.mark.idempotent_id('1b1a0953-a772-4cfe-a7da-2f6de950123')
# def test_contrail_node_status(client_contrail, contrail_node_role):
#     print('Check contrail node %s status' % contrail_node_role)
