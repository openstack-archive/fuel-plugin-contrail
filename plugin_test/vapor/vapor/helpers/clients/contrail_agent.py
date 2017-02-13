import urllib2
import xmltodict

from vapor.settings import logger as LOGGER


__all__ = ['ContrailVRouterAgentClient']


class ClientContrailVRouterAgentBase(object):
    def __init__(self, agent_ip, agent_port):
        self.ip = agent_ip
        self.port = agent_port

    def get_snh_dict_data(self, data):
        key = data.keys()
        if key[0].find(r'__') == 0:
            data = data[key[0]]
        data = self.del_unused_key(data)
        return_dict = {}
        key = data.keys()
        for i in key:
            return_dict[i] = self.get_data(data[i])
        return return_dict

    def get_resource(self, path):
        url = 'http://%s:%s/%s' % (self.ip, self.port, path)
        req = urllib2.Request(url)
        try:
            response = urllib2.urlopen(req)
            xmldata = response.read()
        except Exception, e:
            LOGGER.error('get_xml exception: {} url: {}'.format(e, url))
        xml_dict = xmltodict.parse(xmldata)
        return xml_dict

    @staticmethod
    def del_unused_key(data):
        key_list = ['@type', '@identifier', '@size', 'more',
                    'Pagination', 'OvsdbPageResp', 'next_batch']
        for i in key_list:
            try:
                del data[i]
            except KeyError:
                pass
        return data

    def get_data(self, data):
        if type(data) == list:
            data_list = []
            for i in data:
                data_dict = self.get_data(i)
                data_list.append(data_dict)
            return_data = data_list
        elif type(data) != list:
            if data.has_key('@type'):
                if data['@type'] == 'sandesh':
                    sandesh_dict = {}
                    data = self.del_unused_key(data)
                    key = data.keys()
                    for i in key:
                        sandesh_dict[i] = self.get_data(data[i])
                    return_data = sandesh_dict
                elif data['@type'] == 'list':
                    data = self.del_unused_key(data)
                    key = data.keys()
                    data = data[key[0]]
                    return_data = self.get_data(data)
                elif data['@type'] == 'struct':
                    return_list = []
                    data = self.del_unused_key(data)
                    if len(data) == 0:
                        return ''
                    keys = data.keys()
                    for i in keys:
                        sdata = self.get_data(data[i])
                    return_data = sdata
                elif data['@type'] in ['i64', 'i32', 'i16', 'u64', 'u32', 'u16', 'double', 'string', 'bool']:
                    if data.has_key('#text'):
                        return_data = data['#text']
                    else:
                        return_data = ''
            elif data.has_key('element'):
                return_data = data['#text']
            else:
                data_dict = {}
                data = self.del_unused_key(data)
                for i in data:
                    data_dict[i] = self.get_data(data[i])
                return_data = data_dict
        return return_data

    def get_snhdict(self, path):
        data = self.get_resource(path)
        all_path = ''
        try:
            top_key = data.keys()
            url = data[top_key[0]]['Pagination']['req']['PageReqData']['all']['#text']
            all_path = 'Snh_PageReq?x=%s' % (url)
        except KeyError:
            pass
        try:
            top_key = data.keys()
            url = data[top_key[0]]['OvsdbPageResp']['req']['OvsdbPageRespData']['all']['#text']
            all_path = 'Snh_OvsdbPageReq?x=%s' % (url)
        except KeyError:
            pass
        if all_path != '':
            data = self.get_resource(all_path)
        keys = data.keys()
        if data[keys[0]].has_key('next_batch') == True:
            while True:
                if data[keys[0]].has_key('next_batch') == True:
                    old_data = data.copy()
                    path1 = data[keys[0]]['next_batch']['@link']
                    path2 = data[keys[0]]['next_batch']['#text']
                    path = 'Snh_%s?x=%s' % (path1,path2)
                    data = self.get_resource(path)
                    old_list = self.find_ifmap_list(old_data)
                    self.merge_ifmap_list(data, old_list)
                else:
                    break
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



