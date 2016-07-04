from socketIO_client import SocketIO


class SocketIOClient(SocketIO):
    """
    Fix for library bug
    """

    def _should_stop_waiting(self, for_connect=False, for_callbacks=False):
        if for_connect:
            for namespace in self._namespace_by_path.values():
                is_namespace_connected = getattr(
                    namespace, '_connected', False)
                #Added the check and namespace.path
                #because for the root namespaces, which is an empty string
                #the attribute _connected is never set
                #so this was hanging when trying to connect to namespaces
                # this skips the check for root namespace, which is implicitly connected
                if not is_namespace_connected and namespace.path:
                    return False
            return True
        if for_callbacks and not self._has_ack_callback:
            return True
        return super(SocketIO, self)._should_stop_waiting()