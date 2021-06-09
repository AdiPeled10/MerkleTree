# Adi Peled, 318814308, Itamar Fisch, 312502602
import math
import base64
from MerkleNode import MerkleBinaryNode
import RSAsignature


class BinaryMerkleTree:
    def __init__(self):
        self.root = None
        self.leaves = []

    def get_root_key(self):
        if self.root is None:
            return ''
        return self.root.data

    def add_leaf(self, node: MerkleBinaryNode):
        self.leaves.append(node)
        if len(self.leaves) == 1:
            self.root = node
            return 1
        inserted_node_parent = MerkleBinaryNode(None, None, 0)

        # check if current tree is complete
        if is_power_of_2(len(self.leaves) - 1):
            inserted_node_parent.triangle_binding(self.root, node)
            self.root = inserted_node_parent
        else:
            # find first node with incomplete right subtree
            curr_node = self.leaves[-2]  # the previous last leaf
            while curr_node.parent.height == curr_node.height + 1:
                curr_node = curr_node.parent

            # Add the node to the tree
            curr_node.parent.right_binding(inserted_node_parent)
            inserted_node_parent.triangle_binding(curr_node, node)

        # updating all keys in the path to the new node
        inserted_node_parent.node_diffusion()

    def inorder_traversal(self):
        self.root.inorder_print()


def print_error(msg) :
    # TODO before submit make sure to replace the code with "print('')"
    # This function will help us make all the prints disappear before submit
    print(msg)


def is_power_of_2(n: int):
    if n == 0:
        return False
    n_minus_one = n - 1
    return (n & n_minus_one) == 0


def case1(merkle_tree, user_input):
    data = user_input[2:]
    node = MerkleBinaryNode(None, None, data)
    merkle_tree.add_leaf(node)


def case2(merkle_tree):
    print(merkle_tree.get_root_key())


merkle_tree = BinaryMerkleTree()
sign_algo = RSAsignature.RSAsignature
while True:
    user_input = input()
# for i in range(20):
#     user_input = '1 ' + chr(ord('a') + i)
    option = user_input[0]
    if option == '1':
        case1(merkle_tree, user_input)
    elif option == '2':
        case2(merkle_tree)
    elif option == '5':
        sk, vk = sign_algo.generate()
        print(sk)
        print(vk)
    elif option == '6':
        user_input = '''6 -----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA1MAmLr5TwN8OnQF9OjfWGyGuHfl5056u7XBjYcsidkQHVLkK
8NhFzSvBnQbi18PcXVSLusLPVnGs6a9rfN9NkCM6uSom0+lpFgMWuD/7w0HPIW7C
w0hVlFNWvZ8vv5uzA/mzpF8S1fRmCMkfQyP4TDJ2MImQxcdkWDpFDq1pmvRJweav
zUnc2eUmuz4bwLYwv3CBKDlCSdIAFCkVP6PJl8cbZkOPqbVPMW+MLf+pZrKfWczC
xCnzHmLbzngClQp+4meAtGOGgKKwsmS1eA0BAYfao0g+cu1ESU5ePea/jrX0nJON
vDOAeh00keQvxE1xoEnKppbKT2F6RTyBITbCmwIDAQABAoIBAH0iQ5MMyVBRIlRA
svpSKzGsHrBsszZASF1J1HqJs0xiePlhGUlNu8iQqwGEMlp8ThnrB4Ci4rbSh8Sv
NAavhPx5bCnK3CmaSP/0cyGOKLPQ+laMwiuAWS2z0voXLkuB9copzXqpnPeRF46l
VSj1eC7BI3krAKcDv0aRh1q5rrq/T3sH76nENwjxRVig9wZ1jWNBqpWD7LOx2M8I
NcW4ZbcALbREzKEyydZ1BBx0FXMYyeJRvRdmLzNCb7RZ/wz4B/1bSoUUi8mTBF6x
ft6fZ6JQNak9r2PEvc7eh+FWoDF3Gu3PBFb0poX7SdWWle9qG6efTSiavUo+cetS
Qb0qV4kCgYEA+weJpApGEqxKwCe8oN+pd42QOmnKEzqQlZ33pSP97VmOQj6GcXfu
onnH/0hu4jozj5N96kOCDjDPdpCOvUgzupJBhiRr1M/4y8f+SoWrRCuHHscnfh5Q
pv+iwpSHTcV8ys2fGowpmd9tZfGerJkvAcD/3jG1Mo+0anemHAoCbXUCgYEA2PaT
rBVXKJovd9ZjPqWX7MWhTh1NFGCquQPe4cX5h8wIgjSBqozsosKzKYHmK/kw7yU/
P9UvCiEbiowPiqDZoSbZ6twpf2bcXjaVKWdRqFD+OvGXEvpPVvdbRUXv0J9UDsd1
EDM5/lX6Sja54ibIKP+okcjH3YPd4xbRvZoyHc8CgYARJgGsGBuTWPu+RrinEMBl
72DD7MgmKiEIZ4MsX9oP5cdHFThf9f5yUPltoggZIjq1ezDl2PjAeWsiwVtO6OjH
vQgG3uQS5KYtXZssghciEAsp+hbjkbSWw+3ddwILOQt+Wy+cQ6jv3wh9J1VcmxZP
+1w/VIv5SUHc6BGL5s8lpQKBgQC4zfdlOdw+0m6iZfOtNgHdhU1rqxuvwtNIutpL
d4WfvRR2S+Ey88zQqoVPUr1LMXwUB6cDaUQjHaZG8hx+2ZnmYaB3I8cZJPWKLnYJ
iV8Nvsd+T7B+UsXn7tRIglTOYBiKaiz1epzoXjXOpyTYVG5kNbhRTTOpJJyIxTQs
iz4rEwKBgBxxJ6t4F8APkYkXaY5EB/Z6EtJJDbKgoqBkfWuVZ0DzPBmVKUbP6EKM
T085EM/HlQer1QQjfkdepVuCL7mdDjKcxVMiuMKPWtVlsJjtJMa11smmdqZ5UT/w
6R54/knAIkDXNlGE2xBXCcfKdhF2+lICi5COWEQk5NASSVdgfKjN
-----END RSA PRIVATE KEY-----'''
        sk_bytes = user_input[2:].encode('ASCII')
        data = merkle_tree.get_root_key().encode('ASCII')
        sign = sign_algo.sign(data, sk_bytes)
        print(sign)
    elif user_input[0] == '7':
        user_input = '''7 -----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA1MAmLr5TwN8OnQF9OjfW
GyGuHfl5056u7XBjYcsidkQHVLkK8NhFzSvBnQbi18PcXVSLusLPVnGs6a9rfN9N
kCM6uSom0+lpFgMWuD/7w0HPIW7Cw0hVlFNWvZ8vv5uzA/mzpF8S1fRmCMkfQyP4
TDJ2MImQxcdkWDpFDq1pmvRJweavzUnc2eUmuz4bwLYwv3CBKDlCSdIAFCkVP6PJ
l8cbZkOPqbVPMW+MLf+pZrKfWczCxCnzHmLbzngClQp+4meAtGOGgKKwsmS1eA0B
AYfao0g+cu1ESU5ePea/jrX0nJONvDOAeh00keQvxE1xoEnKppbKT2F6RTyBITbC
mwIDAQAB
-----END PUBLIC KEY-----
'''
        pub_key = user_input[2:]
        # user_input = input()
        user_input = '''LhnptHJUc4M0GVZR+wbp5NC6owLwH2+N/UpOKV6jnyH8iA8YoVSQkMU63z8QZyr50L1f4hTWSxZbjzeQ1Rm/1OyAyX9QdQHIrMWRjOx0GPfqPi4wmcmF9ZxPr7ShwRZtbqz9mAekKYDell44Pj21xKsFFy4PgpnxrXFNppPOA3ZpQk245bYPIdzYpcmq0FyYx5RQQCQYBV69QrQOAvvkVVkwZbiqI0/+tZWmfNdV/x6E3PWYljSccMLW/m4nhcy+XQ39Q2oxIzYlobwndW3epxEReLzP7qeN9BR/BVew2yCn4quhm1fA7544mpZaW0VynQDRHBy7gqJDhuWRLjKOcQ== ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb'''
        sign_len = user_input.find(' ')
        sign = user_input[:sign_len]
        signed_text = user_input[sign_len + 1:].encode('ASCII')
        print(sign_algo.verify(signed_text, pub_key, sign))




# merkle_tree.inorder_traversal()

