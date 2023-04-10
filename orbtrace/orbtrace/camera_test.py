from migen import *
from litex.soc.interconnect.csr import *
from litex.soc.interconnect import wishbone

class WishboneWriteModule(Module, AutoCSR):
    def __init__(self, addr, threshold=0x20000, width=32):

        mem = Memory( 32, threshold )
        self.specials.port = mem.get_port( write_capable=True )
        
        # attach a wishbone interface to the Memory() object, with a read-only port
        self.submodules.wb_sram_if = wishbone.SRAM(mem, read_only=False)
        
        # get the wishbone Interface accessor object
        self.bus = wishbone.Interface()
        
        # build an address filter object. This is a migen expression returns 1
        # when the address "a" matches the RAM address space. Useful for precisely
        # targeting the RAM relative to other wishbone-connected objects within
        # the logic, e.g. other RAM blocks or registers.
        # 
        # This filter means the RAM object will occupy its entire own CSR block,
        # with aliased copies of the RAM filling the entire block
        def slave_filter(a):
            return 1
        # This filter constrains the RAM to just its own address space
        decoder_offset = log2_int(threshold, need_pow2=False)
        def slave_filter_noalias(a):
            return a[decoder_offset:32 - decoder_offset] == 0
        
        # connect the Wishbone bus to the Memory wishbone port, using the address filter
        # to help decode the address.
        # The decdoder address filter as a list with entries as follows:
        #   (filter_function, wishbone_interface.bus)
        # This is useful if you need to attach multiple local logic memories into the
        # same wishbone address bank.
        wb_con = wishbone.Decoder(self.bus, [(slave_filter, self.wb_sram_if.bus)], register=True)
        # add the decoder as a submodule so it gets pulled into the finalize sweep
        self.submodules += wb_con



        ##########################################################################################


        self.count = CSRStorage(width, description="Counter increment value", reset=0x1)
        self.threshold = CSRStorage(width, description="Counter threshold value", reset=threshold)
        self.addr = CSRStatus(self.bus.adr_width, description="Memory address for count value", reset=addr)
        self.value = CSRStatus(width, description="Current counter value", reset=0x0)
        self.write_count_csr = CSRStatus(width, description="Write Counter CSR", reset=0x0)
        self.write_addr = CSRStatus(width, description="Write Counter CSR", reset=0x0)
        

        # create a counter signal and add an incrementing logic
        self.write_count = Signal(width) # Number of times we have written to memory

        self.counter = Signal(width)
        self.addr_write = Signal(width)

        # add a logic to read the current counter value
        self.comb += self.value.status.eq(self.counter)
        self.comb += self.write_count_csr.status.eq(self.write_count)
        self.comb += self.addr_write.eq(self.addr.status + (self.counter))
        self.comb += self.write_addr.status.eq(self.bus.adr)


        # print("Test!!!!!!!!!!!!!!")

        self.submodules.fsm = fsm = FSM(reset_state="IDLE")
        fsm.act("IDLE",
            NextValue(self.port.adr, self.counter),
            NextState("WRITE")
        )
        fsm.act("WRITE",
            NextValue(self.port.dat_w, self.counter),
            NextValue(self.port.we, 1),
            NextState("DONE")
        )
        fsm.act("DONE",
            # NextValue(self.port.we, 0),
            
            If(self.threshold.storage > self.counter, 
                    NextValue(self.counter, self.counter + self.count.storage)
                ).Else(
                    NextValue(self.counter, 0)
                ),
            NextState("IDLE")
        )

        