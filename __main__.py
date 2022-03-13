"""Main module. Start main_service with different broker and handler."""
from pwsh_handler import PowerShellHandler
from service_framework.service_async import launch_service

if __name__ == '__main__':

    launch_service(
        callback_handler=PowerShellHandler,
    )
