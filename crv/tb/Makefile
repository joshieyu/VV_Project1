# Project 1 random-only testbench. Run from repo root:
#   make -C crv/tb SIM=icarus CRV_MODE=uniform CRV_SEED=4701 CRV_CYCLES=256
#   make -C crv/tb SIM=icarus CRV_MODE=tuned CRV_SEED=4701 CRV_CYCLES=2048
TOPLEVEL_LANG ?= verilog
SIM           ?= icarus

DUT ?= $(CURDIR)/../../dut/fifo.sv
VERILOG_SOURCES = $(DUT)
TOPLEVEL = fifo
MODULE   = test_crv

export PYTHONPATH := $(CURDIR)/../../lib:$(CURDIR)/../../tb/fifo:$(CURDIR)/..:$(PYTHONPATH)

include $(shell cocotb-config --makefiles)/Makefile.sim
