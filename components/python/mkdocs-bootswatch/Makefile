#
# CDDL HEADER START
#
# The contents of this file are subject to the terms of the
# Common Development and Distribution License (the "License").
# You may not use this file except in compliance with the License.
#
# You can obtain a copy of the license at usr/src/OPENSOLARIS.LICENSE
# or http://www.opensolaris.org/os/licensing.
# See the License for the specific language governing permissions
# and limitations under the License.
#
# When distributing Covered Code, include this CDDL HEADER in each
# file and include the License file at usr/src/OPENSOLARIS.LICENSE.
# If applicable, add the following below this CDDL HEADER, with the
# fields enclosed by brackets "[]" replaced with your own identifying
# information: Portions Copyright [yyyy] [name of copyright owner]
#
# CDDL HEADER END
#
# Copyright 2016, Aurelien Larcher.
#
include ../../../make-rules/shared-macros.mk


COMPONENT_NAME= mkdocs-bootswatch
COMPONENT_VERSION= 0.4.0
COMPONENT_FMRI= library/python/mkdocs-bootswatch
COMPONENT_PROJECT_URL= http://mkdocs.github.io/mkdocs-bootswatch/
COMPONENT_SRC= $(COMPONENT_NAME)-$(COMPONENT_VERSION)
COMPONENT_ARCHIVE= $(COMPONENT_SRC).tar.gz
COMPONENT_ARCHIVE_HASH=	\
    sha256:51d1305d5ab7240983412611828e657598a73bb97df7d5da839e2ef7bfd827db
COMPONENT_ARCHIVE_URL= \
    https://github.com/mkdocs/mkdocs-bootswatch/archive/$(COMPONENT_VERSION).tar.gz

PYTHON_VERSIONS=	2.7

include $(WS_TOP)/make-rules/prep.mk
include $(WS_TOP)/make-rules/setup.py.mk
include $(WS_TOP)/make-rules/ips.mk

build:		$(BUILD_NO_ARCH)

install:	$(INSTALL_NO_ARCH)

test:		$(NO_TESTS)

REQUIRED_PACKAGES += runtime/python-27
