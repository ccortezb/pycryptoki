"""
Functions for managing partitions
"""
from _ctypes import pointer
from ctypes import byref, c_ubyte
import logging
from pycryptoki.cryptoki import (CK_SLOT_ID,
                                 CK_ULONG,
                                 CK_SESSION_HANDLE,
                                 CA_CreateContainer,
                                 CA_DeleteContainerWithHandle,
                                 CA_GetContainerList,
                                 CA_GetContainerCapabilitySet,
                                 CA_GetContainerCapabilitySetting,
                                 CA_GetContainerPolicySet,
                                 CA_GetContainerPolicySetting,
                                 CA_GetContainerName,
                                 CA_GetContainerStorageInformation,
                                 CA_GetContainerStatus,
                                 CA_SetContainerPolicy,
                                 CA_SetContainerPolicies,
                                 CA_SetContainerSize)
from pycryptoki.defines import (LUNA_PARTITION_TYPE_STANDALONE,
                                LUNA_CF_CONTAINER_ENABLED,
                                LUNA_CF_KCV_CREATED,
                                LUNA_CF_LKCV_CREATED,
                                LUNA_CF_HA_INITIALIZED,
                                LUNA_CF_PARTITION_INITIALIZED,
                                LUNA_CF_CONTAINER_ACTIVATED,
                                LUNA_CF_CONTAINER_LUSR_ACTIVATED,
                                LUNA_CF_USER_PIN_INITIALIZED,
                                LUNA_CF_SO_PIN_LOCKED,
                                LUNA_CF_SO_PIN_TO_BE_CHANGED,
                                LUNA_CF_USER_PIN_LOCKED,
                                LUNA_CF_LIMITED_USER_PIN_LOCKED,
                                LUNA_CF_LIMITED_USER_CREATED,
                                LUNA_CF_USER_PIN_TO_BE_CHANGED,
                                LUNA_CF_LIMITED_USER_PIN_TO_BE_CHANGED)
from pycryptoki.common_utils import AutoCArray, refresh_c_arrays
from pycryptoki.test_functions import make_error_handle_function


LOG = logging.getLogger(__name__)


def ca_create_container(h_session, storage_size, password=None, label='Inserted Token'):
    """Inserts a token into a slot without a Security Officer on the token

    :param h_session: Current session
    :param storage_size: The storage size of the token (0 for undefined/unlimited)
    :param password: The password associated with the token (Default value = 'userpin')
    :param label: The label associated with the token (Default value = 'Inserted Token')
    :returns: The result code, The container number

    """
    h_sess = CK_SESSION_HANDLE(h_session)
    h_container = CK_ULONG()
    LOG.info("CA_CreateContainer: Inserting token with no SO storage_size=" + str(
        storage_size) + ", pin=" + str(password) + ", label=" + label)

    if password == '':
        password = None

    password = AutoCArray(data=password)
    label = AutoCArray(data=label)

    ret = CA_CreateContainer(h_sess, CK_ULONG(0),
                             label.array, label.size.contents,
                             password.array, password.size.contents,
                             CK_ULONG(-1), CK_ULONG(-1), CK_ULONG(0), CK_ULONG(0),
                             CK_ULONG(storage_size), byref(h_container))
    LOG.info("CA_CreateContainer: Inserted token into slot " + str(h_container.value))
    return ret, h_container.value


ca_create_container_ex = make_error_handle_function(ca_create_container)


def ca_delete_container_with_handle(h_session, h_container):
    """
    Delete a container by handle

    :param h_session: session
    :param h_container: target container handle
    """
    h_sess = CK_SESSION_HANDLE(h_session)
    container_id = CK_ULONG(h_container)
    LOG.info(
        "CA_DeleteContainerWithHandle: "
        "Attempting to delete container with handle: %s", h_container)

    ret = CA_DeleteContainerWithHandle(h_sess, container_id)

    LOG.info("CA_DeleteContainerWithHandle: Ret Value: %s", ret)

    return ret


ca_delete_container_with_handle_ex = make_error_handle_function(ca_delete_container_with_handle)


def ca_get_container_list(slot, group_handle=0, container_type=LUNA_PARTITION_TYPE_STANDALONE):
    """
    """
    slot_id = CK_SLOT_ID(slot)
    group = CK_ULONG(group_handle)
    cont_type = CK_ULONG(container_type)
    cont_handles = AutoCArray()

    @refresh_c_arrays(1)
    def _get_cont_list():
        """Closer for retries to work w/ properties
        """
        return CA_GetContainerList(slot_id, group, cont_type,
                                   cont_handles.array, cont_handles.size)

    ret = _get_cont_list()

    return ret, list(cont_handles.array)


ca_get_container_list_ex = make_error_handle_function(ca_get_container_list)


def ca_get_container_capability_set(slot, h_container):
    """
    Get the container capabilities of the given slot.

    :param int slot: target slot number
    :param int h_container: target container handle
    :return: retcode, {id: val} dict of capabilities (None if command failed)
    """
    slot_id = CK_SLOT_ID(slot)
    cont_id = CK_ULONG(h_container)
    cap_ids = AutoCArray()
    cap_vals = AutoCArray()

    @refresh_c_arrays(1)
    def _get_container_caps():
        """Closer for retries to work w/ properties
        """
        return CA_GetContainerCapabilitySet(slot_id,
                                            cont_id,
                                            cap_ids.array,
                                            cap_ids.size,
                                            cap_vals.array,
                                            cap_vals.size)

    ret = _get_container_caps()

    return ret, dict(zip(cap_ids, cap_vals))


ca_get_container_capability_set_ex = make_error_handle_function(ca_get_container_capability_set)


def ca_get_container_capability_setting(slot, h_container, capability_id):
    """
    Get the value of a container's single capability

    :param slot: slot ID of slot to query
    :param h_container: target container handle
    :param capability_id: capability ID
    :return: result code, CK_ULONG representing capability active or not
    """
    slot_id = CK_SLOT_ID(slot)
    cont_id = CK_ULONG(h_container)
    cap_id = CK_ULONG(capability_id)
    cap_val = CK_ULONG()
    ret = CA_GetContainerCapabilitySetting(slot_id,
                                           cont_id,
                                           cap_id,
                                           pointer(cap_val))
    return ret, cap_val.value


ca_get_container_capability_setting_ex = make_error_handle_function(ca_get_container_capability_setting)


def ca_get_container_policy_set(slot, h_container):
    """
    Get the policies of the given slot and container.

    :param int slot: target slot number
    :param int h_container: target container handle
    :return: retcode, {id: val} dict of policies (None if command failed)
    """
    slot_id = CK_SLOT_ID(slot)
    cont_id = CK_ULONG(h_container)
    pol_ids = AutoCArray()
    pol_vals = AutoCArray()

    @refresh_c_arrays(1)
    def _ca_get_container_policy_set():
        """Closure for retries.
        """
        return CA_GetContainerPolicySet(slot_id,
                                  cont_id,
                                  pol_ids.array,
                                  pol_ids.size,
                                  pol_vals.array,
                                  pol_vals.size)

    ret = _ca_get_container_policy_set()

    return ret, dict(zip(pol_ids, pol_vals))


ca_get_container_policy_set_ex = make_error_handle_function(ca_get_container_policy_set)


def ca_get_container_policy_setting(slot, h_container, policy_id):
    """
    Get the value of a container's single policy

    :param slot: slot ID of slot to query
    :param h_container: target container handle
    :param policy_id: policy ID
    :return: result code, CK_ULONG representing policy active or not
    """
    slot_id = CK_SLOT_ID(slot)
    cont_id = CK_ULONG(h_container)
    pol_id = CK_ULONG(policy_id)
    pol_val = CK_ULONG()
    ret = CA_GetContainerPolicySetting(slot_id, cont_id, pol_id, pointer(pol_val))
    return ret, pol_val.value


ca_get_container_policy_setting_ex = make_error_handle_function(ca_get_container_policy_setting)


def ca_get_container_name(slot, h_container):
    """
    Get a container's name

    :param slot: target slot
    :param h_container: target container handle
    """
    slot_id = CK_SLOT_ID(slot)
    cont_id = CK_ULONG(h_container)
    name_arr = AutoCArray(ctype=c_ubyte)

    @refresh_c_arrays(1)
    def _ca_get_container_name():
        """
        Closure for retries
        """
        return CA_GetContainerName(slot_id,
                                   cont_id,
                                   name_arr.array,
                                   name_arr.size)
    ret = _ca_get_container_name()

    return ret, ''.join(map(chr, name_arr.array))


ca_get_container_name_ex = make_error_handle_function(ca_get_container_name)


def ca_get_container_storage_information(slot, h_container):
    """
    Get a container's storage information

    :param slot: target slot
    :param h_container: target container handle
    """
    slot_id = CK_SLOT_ID(slot)
    cont_id = CK_ULONG(h_container)
    overhead = CK_ULONG()
    total = CK_ULONG()
    used = CK_ULONG()
    free = CK_ULONG()
    obj_count = CK_ULONG()

    ret = CA_GetContainerStorageInformation(slot_id,
                                            cont_id,
                                            pointer(overhead),
                                            pointer(total),
                                            pointer(used),
                                            pointer(free),
                                            pointer(obj_count))
    return ret, {'overhead': overhead.value,
                 'total': total.value,
                 'used': used.value,
                 'free': free.value,
                 'object_count': obj_count.value}


ca_get_container_storage_information_ex = make_error_handle_function(ca_get_container_storage_information)


def ca_get_container_status(slot, h_container):
    """
    Get a container's Status

    :param slot: target slot
    :param h_container: target container handle
    """
    slot_id = CK_SLOT_ID(slot)
    cont_id = CK_ULONG(h_container)
    status_flags = CK_ULONG()
    failed_so_logins = CK_ULONG()
    failed_user_logins = CK_ULONG()
    failed_limited_user_logins = CK_ULONG()

    ret = CA_GetContainerStatus(slot_id,
                                cont_id,
                                pointer(status_flags),
                                pointer(failed_so_logins),
                                pointer(failed_user_logins),
                                pointer(failed_limited_user_logins))
    flags_dict = {
        'container_enabled': LUNA_CF_CONTAINER_ENABLED,
        'kcv_created': LUNA_CF_KCV_CREATED,
        'lkcv_created': LUNA_CF_LKCV_CREATED,
        'ha_initialized': LUNA_CF_HA_INITIALIZED,
        'partition_initialized': LUNA_CF_PARTITION_INITIALIZED,
        'container_activated': LUNA_CF_CONTAINER_ACTIVATED,
        'container_lusr_activated': LUNA_CF_CONTAINER_LUSR_ACTIVATED,
        'user_pin_initialized': LUNA_CF_USER_PIN_INITIALIZED,
        'so_pin_locked': LUNA_CF_SO_PIN_LOCKED,
        'so_pin_to_be_changed': LUNA_CF_SO_PIN_TO_BE_CHANGED,
        'user_pin_locked': LUNA_CF_USER_PIN_LOCKED,
        'limited_user_pin_locked': LUNA_CF_LIMITED_USER_PIN_LOCKED,
        'limited_user_created': LUNA_CF_LIMITED_USER_CREATED,
        'user_pin_to_be_changed': LUNA_CF_USER_PIN_TO_BE_CHANGED,
        'limited_user_pin_to_be_changed': LUNA_CF_LIMITED_USER_PIN_TO_BE_CHANGED
    }
    for key, flag in flags_dict.iteritems():
        flags_dict[key] = 1 if flag & status_flags.value else 0

    failed_logins_dict = {
        'failed_so_logins': failed_so_logins.value,
        'failed_user_logins': failed_user_logins.value,
        'failed_limited_user_logins': failed_limited_user_logins.value
    }
    return ret, flags_dict, failed_logins_dict


ca_get_container_status_ex = make_error_handle_function(ca_get_container_status)


def ca_set_container_policy(h_session, h_containerber, policy_id, policy_val):
    """Sets a policy on the container.

    NOTE: With per partition SO this method should generally not be used. Instead
    ca_set_partition_policies should be used

    :param h_session: The session handle of the entity with permission to change the policy
    :param h_containerber: The container number to set the policy on.
    :param policy_id: The identifier of the policy (ex. CONTAINER_CONFIG_MINIMUM_PIN_LENGTH)
    :param policy_val: The value to set the policy to
    :returns: The result code

    """
    ret = CA_SetContainerPolicy(CK_SESSION_HANDLE(h_session),
                                CK_ULONG(h_containerber),
                                CK_ULONG(policy_id),
                                CK_ULONG(policy_val))
    return ret


ca_set_container_policy_ex = make_error_handle_function(ca_set_container_policy)


def ca_set_container_policies(h_session, h_container, policies):
    """
    Set multiple container policies.

    :param h_session: session handle
    :param h_container: target container handle
    :param policies: dict of policy ID ints and value ints
    :return: result code
    """
    h_sess = CK_SESSION_HANDLE(h_session)
    container_id = CK_ULONG(h_container)
    pol_id_list = policies.keys()
    pol_val_list = policies.values()
    pol_ids = AutoCArray(data=pol_id_list, ctype=CK_ULONG)
    pol_vals = AutoCArray(data=pol_val_list, ctype=CK_ULONG)

    ret = CA_SetContainerPolicies(h_sess,
                                  container_id,
                                  pol_ids.size.contents,
                                  pol_ids.array,
                                  pol_vals.array)

    return ret


ca_set_container_policies_ex = make_error_handle_function(ca_set_container_policies)


def ca_set_container_size(h_session, h_container, size):
    """
    Set a container's size

    :param h_session: session handle
    :param h_container: target container handle
    :param size: size
    :return: result code
    """
    h_sess = CK_SESSION_HANDLE(h_session)
    container_id = CK_ULONG(h_container)
    size = CK_ULONG(size)
    ret = CA_SetContainerSize(h_sess,
                              container_id,
                              size)
    return ret


ca_set_container_size_ex = make_error_handle_function(ca_set_container_size)
