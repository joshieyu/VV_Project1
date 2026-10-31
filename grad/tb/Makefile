# Random-only regression for the graduate-extension analysis.
#   make SIM=icarus GRAD_STIM=phased GRAD_SEED=1 GRAD_CYCLES=256
# Reuses the driver, monitor, env, and scoreboard from tb/fifo.
TOPLEVEL_LANG ?= verilog
SIM           ?= icarus

DUT ?= $(CURDIR)/../../dut/fifo.sv
VERILOG_SOURCES = $(DUT)
TOPLEVEL = fifo
MODULE   = test_grad

export PYTHONPATH := $(CURDIR)/../../lib:$(CURDIR)/../../tb/fifo:$(CURDIR)/..:$(PYTHONPATH)

include $(shell cocotb-config --makefiles)/Makefile.sim
