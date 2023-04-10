from migen import *
from litex.soc.interconnect.csr import *
from litex.soc.interconnect import wishbone

class ADCModule(Module, AutoCSR):
    def __init__(self, addr, cmp, mem_size=0x8, width=32,):

        mem = Memory( 32, mem_size )
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
        decoder_offset = log2_int(mem_size, need_pow2=False)
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

        self.average = CSRStatus(width, description="Average ADC Values", reset=0x0)
        self.threshold = CSRStorage(width, description="Counter threshold value", reset=mem_size)

        self.enable_sub = Signal()
        self.sub_count = Signal(width)

        self.rst = Signal()
        
        
        self.digital_out = Signal(8)



        self.cmp = cmp
        
        self.analog_out = Signal()
        self.rdy = Signal()

        self.counter = Signal(width)

        self.running_sum = Signal(width + 4) # Add some lee-way


        self.specials += Instance("ADC_top", 
                                        i_clk_in = ClockSignal('adc'), 
                                        i_rstn = self.rst, 
                                        i_analog_cmp = self.cmp, 
                                        o_digital_out = self.digital_out, 
                                        o_analog_out = self.analog_out, 
                                        o_sample_rdy = self.rdy)



        self.submodules.fsm = fsm = FSM(reset_state="IDLE")
        fsm.act("IDLE",
            NextValue(self.port.adr, self.counter),
            If(self.rdy, 
                NextState("WRITE")
            )
        )
        fsm.act("WRITE",
            NextValue(self.port.dat_w, self.digital_out),
            NextValue(self.port.we, 1),
            NextValue(self.running_sum, self.running_sum + self.digital_out),
            NextState("DONE")
        )
        fsm.act("DONE",
            NextValue(self.port.we, 0),
            
            If(mem_size > self.counter, 
                    NextValue(self.counter, self.counter + 1)
                ).Else(
                    NextValue(self.counter, 0),
                    NextValue(self.enable_sub,1)
                ),
            NextState("IDLE")
        )

        