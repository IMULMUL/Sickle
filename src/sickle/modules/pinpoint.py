import sys
import binascii

from sickle.formats import (
    c,
    cs,
    bash,
    java,
    nasm,
    perl,
    ruby,
    python,
    python3,
    powershell,
)

from sickle.common.handlers.format_handler import FormatHandler

from sickle.common.lib.generic.convert import from_hex_to_raw

from sickle.common.lib.generic.colors import Colors
from sickle.common.lib.generic.colors import ansi_ljust

from sickle.common.lib.reversing.disassembler import Disassembler

class Module():

    name = "Pinpoint"

    module = "pinpoint"

    example_run = f"{sys.argv[0]} -r shellcode -b \"\\x00\\x0a\\x0d\" -m {module} -a x64 -f c"

    platform = "Multi"

    arch = "Multi"

    ring = "N/A"

    author = ["wetw0rk"]

    tested_platforms = ["Linux"]

    summary = ("Highlights opcodes within a disassembly to identify instructions responsible"
               " for bad characters")

    description = (" Often when crafting shellcode for the x86 architecture your shellcode may"
                   " contain bad characters. Often looking at a bunch of bytes can be difficult, so"
                   " this module will highlight where in the assembly your bad character is being"
                   " generated.")

    arguments = None

    def __init__(self, arg_object):
        
        self.raw_bytes = arg_object["raw bytes"]
        self.badchrs = arg_object["bad characters"]
        self.varname = arg_object["variable name"]
        self.arch    = arg_object["architecture"]
        self.format  = arg_object["format"]

        try:
            self.fmt_module = FormatHandler(self.format, self.raw_bytes, self.badchrs, self.varname).get_language_formatter()
        except:
            print(f"Module does not support {self.format} format\n")
            exit(-1)

        lang_info    = self.fmt_module.get_language_information()
        self.comment = lang_info["single line comment"]
        self.op_esc  = lang_info["opcode escape"]

        self.modes   = Disassembler.get_cs_arch_modes()

    def commented(self):
        
        opcode_string     = []
        instruction_line  = []
        hex_opcode_string = []

        mode = self.modes[self.arch]

        # seperate the instructions and opcode
        for i in mode.disasm(self.raw_bytes, 0x1000):
            opcode_string += "{:s}".format(binascii.hexlify(i.bytes).decode('utf-8')),
            instruction_line += "{:s} {:s}".format(i.mnemonic, i.op_str),

        # hex-ify the opcode string
        for i in range(len(opcode_string)):
            line = opcode_string[i]
            
            #self.fmt_module.robject, self.fmt_module.eobject = hex_to_objects(line)
            self.fmt_module.raw_bytes = from_hex_to_raw(line)

            hex_opcode_string += self.fmt_module.get_generated_lines(True, True)[0],
            ID = Colors.BOLD and Colors.RED and Colors.END

        return [instruction_line, hex_opcode_string, ID]

    def do_thing(self):
        
        instruction_line, hex_opcode_string, ID = self.commented()
        id_Colors = [Colors.BOLD, Colors.RED, Colors.END]
        completed_conversion = []
        results = []

        # We need to get the longest opcode string WITHOUT any bad character formatting. Since
        # this module outputs the string with "analysis", if this information is not accounted
        # for the output will appear mangled.
        raw_opcode_string = hex_opcode_string[0]
        for i in range(len(id_Colors)):
            raw_opcode_string = raw_opcode_string.replace(id_Colors[i], '')

        ll = len(raw_opcode_string)
        for i in range(len(hex_opcode_string)):
            raw_opcode_string = hex_opcode_string[i]
            for j in range(len(id_Colors)):
                raw_opcode_string = raw_opcode_string.replace(id_Colors[j], '')

            if len(raw_opcode_string) > ll:
                ll = len(raw_opcode_string)

        # Format the output
        for i in range(len(instruction_line)):
            if ID in hex_opcode_string[i]:
                if (',' in self.badchrs):
                    bad_char_list = self.badchrs.split(',')
                else:
                    bad_char_list = [self.badchrs]

                bad_char_size = len(bad_char_list[0])
                matches = hex_opcode_string[i].count(Colors.END)

                fl = ll #+ spaces

                h = ansi_ljust(f"{hex_opcode_string[i]} ", (fl+1))
                i = f"{Colors.BOLD}{Colors.RED}{self.comment} {instruction_line[i]} {Colors.END}"
                completed_conversion += f"{h}{i}",

            else:
                h = ansi_ljust(f"{hex_opcode_string[i]} ", (ll+1))
                i = f"{self.comment} {instruction_line[i]}"
                completed_conversion += f"{h}{i}",

        for i in range(len(completed_conversion)):
            print(completed_conversion[i])
