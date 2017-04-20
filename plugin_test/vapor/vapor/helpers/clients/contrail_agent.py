import copy

from six.moves.urllib import request
import xmltodict

from vapor.settings import logger


__all__ = ['ContrailVRouterAgentClient']


class ClientContrailVRouterAgentBase(object):
    def __init__(self, agent_ip, agent_port):
        self.ip = agent_ip
        self.port = agent_port

    def get_snh_dict_data(self, data):
        key = next(iter(data.keys()))
        if key.startswith(r'__'):
            data = data[key]
        data = self.del_unused_key(data)
        return {k: self.get_data(v) for k, v in data.items()}

    def get_resource(self, path):
        url = 'http://%s:%s/%s' % (self.ip, self.port, path)
        try:
            response = request.urlopen(url)
            xmldata = response.read()
        except Exception as e:
            logger.error('get_xml exception: {} url: {}'.format(e, url))
            raise
        xml_dict = xmltodict.parse(xmldata)
        return xml_dict

    @staticmethod
    def del_unused_key(data):
        key_list = ['@type', '@identifier', '@size', 'more',
                    'Pagination', 'OvsdbPageResp', 'next_batch']
        return {k: v for (k, v) in data.items() if k not in key_list}

    def get_data(self, data):
        if isinstance(data, list):
            data_list = []
            for item in data:
                data_dict = self.get_data(item)
                data_list.append(data_dict)
            return_data = data_list
        else:
            if '@type' in data:
                if data['@type'] == 'sandesh':
                    data = self.del_unused_key(data)
                    return_data = {k: self.get_data(v)
                                   for k, v in data.items()}
                elif data['@type'] == 'list':
                    data = self.del_unused_key(data)
                    key = next(iter(data.keys()))
                    data = data[key]
                    return_data = self.get_data(data)
                elif data['@type'] == 'struct':
                    is_list = '@size' in data
                    data = self.del_unused_key(data)
                    if len(data) == 0:
                        return ''
                    value = next(iter(data.values()))
                    if is_list and not (isinstance(value, list)):
                        value = [value]
                    return_data = self.get_data(value)
                elif data['@type'] in ['i64', 'i32', 'i16', 'u64', 'u32',
                                       'u16', 'double', 'string', 'bool']:
                    if '#text' in data:
                        return_data = data['#text']
                    else:
                        return_data = ''
            elif 'element' in data:
                return_data = data['#text']
            else:
                data = self.del_unused_key(data)
                return_data = {k: self.get_data(v) for k, v in data.items()}
        return return_data

    def find_ifmap_list(self, data):
        except_keys = ['@type', '@identifier', '@size',
                       'table_size', 'next_batch', 'more']
        for k in data:
            if not isinstance(data[k], list):
                if k not in except_keys:
                    return self.find_ifmap_list(data[k])
            else:
                temp_list = data[k]
                return copy.copy(temp_list)

    def merge_ifmap_list(self, data, next_list):
        except_keys = ['@type', '@identifier', '@size', 'table_size',
                       'next_batch', 'more']
        for k in data:
            if not isinstance(data[k], list):
                if k not in except_keys:
                    return self.merge_ifmap_list(data[k], next_list)
            else:
                data[k] += next_list
        return data

    def get_snhdict(self, path):
        data = self.get_resource(path)
        # Check all data link
        all_path = None
        try:
            top_key = next(iter(data.keys()))
            url = data[top_key]['Pagination']['req']['PageReqData']['all']['#text']  # noqa
            all_path = 'Snh_PageReq?x=%s' % url
        except KeyError:
            pass
        try:
            top_key = next(iter(data.keys()))
            url = data[top_key]['OvsdbPageResp']['req']['OvsdbPageRespData']['all']['#text']  # noqa
            all_path = 'Snh_OvsdbPageReq?x=%s' % url
        except KeyError:
            pass
        if all_path:
            data = self.get_resource(all_path)
        # Check pagination
        key = next(iter(data.keys()))
        while 'next_batch' in data[key]:
            old_data = data.copy()
            path1 = data[key]['next_batch']['@link']
            path2 = data[key]['next_batch']['#text']
            path = 'Snh_%s?x=%s' % (path1, path2)
            data = self.get_resource(path)
            old_list = self.find_ifmap_list(old_data)
            data = self.merge_ifmap_list(data, old_list)
        return data

    def get_path_to_dict(self, path):
        # Return path directory info by dict
        rsp = self.get_snhdict(path)
        snh_data = self.get_snh_dict_data(rsp)
        return snh_data


class ContrailVRouterAgentClient(ClientContrailVRouterAgentBase):

    def get_itfs(self):
        data = self.get_path_to_dict('Snh_ItfReq')
        return data

    def get_itf_by_name(self, interface_name):
        data = self.get_path_to_dict('Snh_ItfReq?x={}'.format(interface_name))
        return data

    def get_sg_list(self):
        data = self.get_path_to_dict('Snh_SgListReq')
        return data
