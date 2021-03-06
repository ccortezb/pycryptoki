"""
Created on Aug 15, 2012

@author: root
"""

import logging

import pytest

from pycryptoki.default_templates import CKM_DES_KEY_GEN_TEMP, CKM_DES3_KEY_GEN_TEMP, \
    CKM_RSA_PKCS_KEY_PAIR_GEN_PUBTEMP, CKM_RSA_PKCS_KEY_PAIR_GEN_PRIVTEMP, CKM_AES_KEY_GEN_TEMP
from pycryptoki.defines import CKM_DES_KEY_GEN, CKM_AES_KEY_GEN, CKM_DES3_KEY_GEN, \
    CKA_USAGE_LIMIT, CKA_USAGE_COUNT, CKM_RSA_PKCS_KEY_PAIR_GEN, CKM_DES3_ECB, \
    CKM_DES_ECB, CKM_RSA_PKCS, CKR_KEY_NOT_ACTIVE, CKM_AES_ECB
from pycryptoki.encryption import c_encrypt, c_encrypt_ex
from pycryptoki.key_generator import c_generate_key_ex, c_generate_key_pair_ex
from pycryptoki.object_attr_lookup import c_get_attribute_value_ex, c_set_attribute_value_ex
from . import config as hsm_config

LOG = logging.getLogger(__name__)


class TestUsageLimitAndCount(object):
    """ """

    @pytest.fixture(autouse=True)
    def setup_teardown(self, auth_session):
        self.h_session = auth_session
        self.admin_slot = hsm_config["test_slot"]

    def test_set_attribute_usage_limit_sym(self):
        """Test: Verify that user is able to set CKA_USAGE_LIMIT attribute on
                  an symmetric crypto object
            Procedure:
            Generate a DES Key
            Use C_SetAttributeValue to set CKA_USAGE_LIMIT to 5
            Use C_getAttributeValue to verify


        """

        LOG.info("Test: Verify that user is able to set CKA_USAGE_LIMIT attribute on \
                  an symmetric crypto object")

        usage_template = {CKA_USAGE_LIMIT: 5}

        h_key = c_generate_key_ex(self.h_session,
                                  mechanism=CKM_DES_KEY_GEN,
                                  template=CKM_DES_KEY_GEN_TEMP)
        LOG.info("Called c-generate: Key handle -%s", h_key)
        usage_limit = 5

        c_set_attribute_value_ex(self.h_session,
                                 h_key, usage_template)

        out_template = c_get_attribute_value_ex(self.h_session, h_key,
                                                template={CKA_USAGE_LIMIT: None})

        usage_val_out = out_template[CKA_USAGE_LIMIT]
        LOG.info("CKA_USAGE_LIMIT reported by C_GetAttributeValue :%s", usage_val_out)
        assert usage_limit == usage_val_out, "reported USAGE LIMIT does not match"

    def test_usage_limit_attribute_check_sym_des(self):
        """Test: Verify that CKA_USAGE_COUNT attribute increments as user
                  use the symmetric crypto object
            Procedure:
            Generate a DES Key
            Use C_SetAttributeValue to set CKA_USAGE_LIMIT to 2
            Use des key twice for encryption
            Use C_getAttributeValue to verify that CKA_USAGE_COUNT is 2


        """
        LOG.info("Test: Verify that CKA_USAGE_COUNT attribute increments as user \
                  use the symmetric crypto object")
        usage_lim_template = {CKA_USAGE_LIMIT: 2}

        usage_count = 2

        h_key = c_generate_key_ex(self.h_session,
                                  mechanism=CKM_DES_KEY_GEN,
                                  template=CKM_DES_KEY_GEN_TEMP)
        LOG.info("Called c-generate: Key handle -%s", h_key)

        c_set_attribute_value_ex(self.h_session,
                                 h_key, usage_lim_template)

        c_encrypt_ex(self.h_session, h_key, b'a' * 2048, mechanism={"mech_type": CKM_DES_ECB})

        c_encrypt_ex(self.h_session, h_key, b'a' * 2048,
                     mechanism={"mech_type": CKM_DES_ECB})

        py_template = c_get_attribute_value_ex(self.h_session, h_key,
                                               template={CKA_USAGE_COUNT: None})

        usage_val_out = py_template[CKA_USAGE_COUNT]
        LOG.info("CKA_USAGE_COUNT reported by C_GetAttributeValue: %s", usage_val_out)

        assert usage_count == usage_val_out, "reported USAGE LIMIT does not match"

    def test_usage_limit_attribute_check_sym_aes(self):
        """Test: Verify that CKA_USAGE_COUNT attribute increments as user
                  use the symmetric crypto object
            Procedure:
            Generate a DES Key
            Use C_SetAttributeValue to set CKA_USAGE_LIMIT to 2
            Use aes key twice for encryption
            Use C_getAttributeValue to verify that CKA_USAGE_COUNT is 2


        """
        LOG.info("Test: Verify that CKA_USAGE_COUNT attribute increments as user \
                  use the symmetric crypto object")
        usage_lim_template = {CKA_USAGE_LIMIT: 2}

        usage_count = 2

        h_key = c_generate_key_ex(self.h_session, mechanism=CKM_AES_KEY_GEN,
                                  template=CKM_AES_KEY_GEN_TEMP)
        LOG.info("Called c-generate: Key handle -" + str(h_key))

        c_set_attribute_value_ex(self.h_session,
                                 h_key, usage_lim_template)
        c_encrypt_ex(self.h_session, h_key, b'a' * 2048, mechanism={"mech_type": CKM_AES_ECB})

        c_encrypt_ex(self.h_session, h_key, b'a' * 2048, mechanism={"mech_type": CKM_AES_ECB})

        py_template = c_get_attribute_value_ex(self.h_session, h_key,
                                               template={CKA_USAGE_COUNT: None})

        usage_val_out = py_template[CKA_USAGE_COUNT]
        LOG.info("CKA_USAGE_COUNT reported by C_GetAttributeValue: %s", usage_val_out)

        assert usage_count == usage_val_out, "reported USAGE LIMIT does not match"

    def test_set_attribute_usage_limit_Assym(self):
        """Test: Verify that user is able to set CKA_USAGE_LIMIT attribute on
                  an assymetric crypto object
            Procedure:
            Generate a RSA key pair
            Use C_SetAttributeValue to set CKA_USAGE_LIMIT to 2 on RSA public key
            Use C_getAttributeValue to verify


        """

        LOG.info("Test: Verify that user is able to set CKA_USAGE_LIMIT attribute on \
                  an assymetric crypto object")
        usage_lim_template = {CKA_USAGE_LIMIT: 2}

        h_pbkey, h_prkey = c_generate_key_pair_ex(self.h_session,
                                                  mechanism=CKM_RSA_PKCS_KEY_PAIR_GEN,
                                                  pbkey_template=CKM_RSA_PKCS_KEY_PAIR_GEN_PUBTEMP,
                                                  prkey_template=CKM_RSA_PKCS_KEY_PAIR_GEN_PRIVTEMP)
        LOG.info(
            "Called c-generate: Public Key handle: %s Private Key Handle: %s", h_pbkey, h_prkey)
        usage_limit = 2

        c_set_attribute_value_ex(self.h_session,
                                 h_pbkey, usage_lim_template)

        py_template = c_get_attribute_value_ex(self.h_session, h_pbkey,
                                               template={CKA_USAGE_LIMIT: None})
        usage_val_out = py_template[CKA_USAGE_LIMIT]
        LOG.info("CKA_USAGE_LIMIT reported by C_GetAttributeValue: %s", usage_val_out)
        assert usage_limit == usage_val_out, "reported USAGE LIMIT does not match"

    def test_usage_limit_attribute_check_Assym(self):
        """Test: Verify that CKA_USAGE_COUNT attribute increments as user
                  use the assymetric crypto object
            Procedure:
            Generate a RSA Key pair
            Use C_SetAttributeValue to set CKA_USAGE_LIMIT to 2
            Use RSA public key twice for encryption
            Use C_getAttributeValue to verify that CKA_USAGE_COUNT is 2


        """

        LOG.info("Test: Verify that CKA_USAGE_COUNT attribute increments as user \
                  use the assymetric crypto object")

        usage_lim_template = {CKA_USAGE_LIMIT: 2}
        usage_count = 2

        h_pbkey, h_prkey = c_generate_key_pair_ex(self.h_session,
                                                  mechanism=CKM_RSA_PKCS_KEY_PAIR_GEN,
                                                  pbkey_template=CKM_RSA_PKCS_KEY_PAIR_GEN_PUBTEMP,
                                                  prkey_template=CKM_RSA_PKCS_KEY_PAIR_GEN_PRIVTEMP)

        LOG.info(
            "Called c-generate: Public Key handle -%s Private Key Handle -%s", h_pbkey, h_prkey)

        c_set_attribute_value_ex(self.h_session,
                                 h_pbkey, usage_lim_template)
        c_encrypt_ex(self.h_session, h_pbkey, b'a' * 20, mechanism={"mech_type": CKM_RSA_PKCS})

        c_encrypt_ex(self.h_session, h_pbkey, b'a' * 20, mechanism={"mech_type": CKM_RSA_PKCS})

        py_template = c_get_attribute_value_ex(self.h_session, h_pbkey,
                                               template={CKA_USAGE_COUNT: None})

        usage_val_out = py_template[CKA_USAGE_COUNT]
        LOG.info("CKA_USAGE_COUNT reported by C_GetAttributeValue: %s", usage_val_out)
        assert usage_count == usage_val_out, "reported USAGE LIMIT does not match"

    def test_set_attribute_usage_count_check_error_CKR_KEY_NOT_ACTIVE_3des(self):
        """Test: Verify that crypto operation returns error CKR_KEY_NOT_ACTIVE
                  if user try to use crypto object more than limit set on CKA_USAGE_LIMIT
            Procedure:
            Generate a 3DES key
            Use C_SetAttributeValue to set CKA_USAGE_LIMIT to 2
            Use RSA public key 3 times for encryption


        """

        LOG.info("Verify that crypto operation returns error CKR_KEY_NOT_ACTIVE \
                  if user try to use crypto object more than limit set on CKA_USAGE_LIMIT")
        usage_lim_template = {CKA_USAGE_LIMIT: 2}

        h_key = c_generate_key_ex(self.h_session,
                                  mechanism=CKM_DES3_KEY_GEN,
                                  template=CKM_DES3_KEY_GEN_TEMP)
        LOG.info("Called c-generate: Key handle -" + str(h_key))

        c_set_attribute_value_ex(self.h_session,
                                 h_key, usage_lim_template)

        c_encrypt_ex(self.h_session, h_key, b'a' * 2048, mechanism={"mech_type": CKM_DES3_ECB})

        c_encrypt_ex(self.h_session, h_key, b'a' * 2048, mechanism={"mech_type": CKM_DES3_ECB})

        return_val, data = c_encrypt(self.h_session, h_key, b'a' * 2048,
                                     mechanism={"mech_type": CKM_DES3_ECB})
        LOG.info("Called C_Encrypt, return code: %s", return_val)

        py_template = c_get_attribute_value_ex(self.h_session, h_key,
                                               template={CKA_USAGE_COUNT: None})

        usage_val_out = py_template[CKA_USAGE_COUNT]
        LOG.info("CKA_USAGE_COUNT reported by C_GetAttributeValue: %s", usage_val_out)

        assert return_val == CKR_KEY_NOT_ACTIVE, "reported error code does not match"

    def test_set_attribute_usage_count_check_error_CKR_KEY_NOT_ACTIVE_rsa(self):
        """Test: Verify that crypto operation returns error CKR_KEY_NOT_ACTIVE
                  if user try to use crypto object more than limit set on CKA_USAGE_LIMIT
            Procedure:
            Generate a RSA Key pair
            Use C_SetAttributeValue to set CKA_USAGE_LIMIT to 2
            Use RSA public key 3 times for encryption


        """

        usage_lim_template = {CKA_USAGE_LIMIT: 2}

        h_pbkey, h_prkey = c_generate_key_pair_ex(self.h_session,
                                                  mechanism=CKM_RSA_PKCS_KEY_PAIR_GEN,
                                                  pbkey_template=CKM_RSA_PKCS_KEY_PAIR_GEN_PUBTEMP,
                                                  prkey_template=CKM_RSA_PKCS_KEY_PAIR_GEN_PRIVTEMP)

        LOG.info(
            "Called c-generate: Public Key handle -%s Private Key Handle - %s", h_pbkey, h_prkey)

        c_set_attribute_value_ex(self.h_session,
                                 h_pbkey, usage_lim_template)

        c_encrypt_ex(self.h_session, h_pbkey, b'a' * 20, mechanism={"mech_type": CKM_RSA_PKCS})

        c_encrypt_ex(self.h_session, h_pbkey, b'a' * 20, mechanism={"mech_type": CKM_RSA_PKCS})

        return_val, data = c_encrypt(self.h_session, h_pbkey, b'a' * 20,
                                     mechanism={"mech_type": CKM_RSA_PKCS})
        LOG.info("Called C_Encrypt, return code: %s", return_val)
        py_template = c_get_attribute_value_ex(self.h_session, h_pbkey,
                                               template={CKA_USAGE_COUNT: None})

        usage_val_out = py_template[CKA_USAGE_COUNT]
        assert return_val == CKR_KEY_NOT_ACTIVE, "reported error code does not match"
