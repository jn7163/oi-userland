#
# This file and its contents are supplied under the terms of the
# Common Development and Distribution License ("CDDL"), version 1.0.
# You may only use this file in accordance with the terms of version
# 1.0 of the CDDL.
#
# A full copy of the text of the CDDL should have accompanied this
# source.  A copy of the CDDL is also available via the Internet at
# http://www.illumos.org/license/CDDL.
#

#
# Copyright 2014 Alexander Pyhalov.  All rights reserved.
#

include ../../../make-rules/shared-macros.mk

COMPONENT_NAME= clang-34
COMPONENT_VERSION= 3.4.2
COMPONENT_REVISION= 5
COMPONENT_SUMMARY= LLVM tools and Clang compiler
COMPONENT_PROJECT_URL = http://llvm.org/
COMPONENT_FMRI= developer/clang-34
COMPONENT_CLASSIFICATION= Development/C
LLVM_NAME= llvm
CLANG_NAME= cfe
COMPONENT_SRC= $(LLVM_NAME)-$(COMPONENT_VERSION).src
COMPONENT_ARCHIVE= $(COMPONENT_SRC).tar.gz
COMPONENT_ARCHIVE_HASH= \
  sha256:17038d47069ad0700c063caed76f0c7259628b0e79651ce2b540d506f2f1efd7
COMPONENT_ARCHIVE_URL= \
  http://llvm.org/releases/$(COMPONENT_VERSION)/$(COMPONENT_ARCHIVE)
COMPONENT_ARCHIVE_1=    $(CLANG_NAME)-$(COMPONENT_VERSION).src.tar.gz
COMPONENT_ARCHIVE_HASH_1= \
    sha256:5ba6f5772f8d00f445209356a7daf83c5bca2da5acd10de517ad2359ae95bc10
COMPONENT_ARCHIVE_URL_1= http://llvm.org/releases/$(COMPONENT_VERSION)/$(COMPONENT_ARCHIVE_1)
COMPONENT_LICENSE= BSD

include $(WS_MAKE_RULES)/prep.mk
include $(WS_MAKE_RULES)/configure.mk
include $(WS_MAKE_RULES)/ips.mk

CONFIGURE_PREFIX= /usr/clang/3.4

PATH=/usr/sbin:/usr/bin:/usr/perl5/bin:/usr/gnu/bin

COMPONENT_POST_UNPACK_ACTION += $(UNPACK) $(USERLAND_ARCHIVES)$(COMPONENT_ARCHIVE_1) && \
	mv $(CLANG_NAME)-$(COMPONENT_VERSION).src $(COMPONENT_SRC)/tools/clang

COMPONENT_PRE_CONFIGURE_ACTION =        (cp -a $(SOURCE_DIR)/* $(@D))

COMPONENT_POST_INSTALL_ACTION = \
for file in `echo $(PROTO_DIR)/$(CONFIGURE_PREFIX)/bin/*`; do \
	elfedit -e 'dyn:runpath $$ORIGIN/../lib' $$file ; \
done && \
for file in `echo $(PROTO_DIR)/$(CONFIGURE_PREFIX)/lib/*.so`; do \
	elfedit -e 'dyn:delete RUNPATH' $$file ; \
	elfedit -e 'dyn:delete RPATH' $$file ; \
done

COMPONENT_TEST_TARGETS = check-all
COMPONENT_TEST_ENV += PATH=/usr/gnu/bin:/usr/bin

build: $(BUILD_32)

install: $(INSTALL_32)

test: $(TEST_32)

REQUIRED_PACKAGES += library/libxml2
REQUIRED_PACKAGES += library/zlib
REQUIRED_PACKAGES += system/library
REQUIRED_PACKAGES += system/library/g++-4-runtime
REQUIRED_PACKAGES += system/library/gcc-4-runtime
REQUIRED_PACKAGES += system/library/math
REQUIRED_PACKAGES += runtime/ocaml
