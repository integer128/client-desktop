# If some executables not available via PATH, you can set paths here or via
# environment variables.
# PATHS SHOULD CONTAIN THE TRAILING SLASH!

BMN_POSIX_BIN_DIR    ?=
BMN_PYTHON_BIN_DIR   ?=
BMN_PYSIDE_BIN_DIR   ?=
BMN_NSIS_BIN_DIR     ?=
BMN_DMGBUILD_BIN_DIR ?=
BMN_APPIMAGE_BIN_DIR ?=

################################################################################
# Platform-specific binaries
################################################################################

ifeq ($(MAKE_VERSION),$(patsubst 4.%,%,$(MAKE_VERSION)))
BAD_MAKE=1
endif
ifneq ($(MAKE_VERSION),$(patsubst 4.0%,%,$(MAKE_VERSION)))
BAD_MAKE=1
endif
ifeq ($(BAD_MAKE), 1)
$(error Makefile requires GNU Make 4.1+, current version is $(MAKE_VERSION))
endif

.LIBPATTERNS =
.SUFFIXES:

ifneq (,$(findstring mingw32,$(MAKE_HOST)))
PLATFORM := mingw32

EXEC_SUFFIX = .exe
NPATH = $(subst /,\,$(1))
MKDIR = if not exist "$(call NPATH,$(1))" mkdir "$(call NPATH,$(1))"
CP =
RM = if exist "$(call NPATH,$(1))" del /F /Q "$(call NPATH,$(1))"
RMDIR = if exist "$(call NPATH,$(1))" rmdir /S /Q "$(call NPATH,$(1))"
ENVSUBST_FILE =
CHMOD_EXEC =

RSYNC = "$(BMN_POSIX_BIN_DIR)rsync.exe" "--rsh=$(BMN_POSIX_BIN_DIR)ssh.exe"
PYTHON = "$(BMN_PYTHON_BIN_DIR)python.exe"
RCC = "$(BMN_PYSIDE_BIN_DIR)pyside6-rcc.exe"
LUPDATE = "$(BMN_PYSIDE_BIN_DIR)pyside6-lupdate.exe"
LRELEASE = "$(BMN_PYSIDE_BIN_DIR)pyside6-lrelease.exe"
MAKENSIS = "$(BMN_NSIS_BIN_DIR)makensis.exe"
DMGBUILD =
APPIMAGETOOL =
else
ifneq (,$(findstring darwin,$(MAKE_HOST)))
PLATFORM := darwin
else ifneq (,$(findstring linux,$(MAKE_HOST)))
PLATFORM := linux
else
$(error Unsupported platform $(MAKE_HOST))
endif

EXEC_SUFFIX =
NPATH = $(1)
MKDIR = $(BMN_POSIX_BIN_DIR)mkdir -p "$(call NPATH,$(1))"
CP = $(BMN_POSIX_BIN_DIR)cp -f "$(call NPATH,$(1))" "$(call NPATH,$(2))"
RM = $(BMN_POSIX_BIN_DIR)rm -f "$(call NPATH,$(1))"
RMDIR = $(BMN_POSIX_BIN_DIR)rm -rf "$(call NPATH,$(1))"
ENVSUBST_FILE = $(BMN_POSIX_BIN_DIR)cat "$(call NPATH,$(1))" | D=$$ $(BMN_POSIX_BIN_DIR)envsubst > "$(call NPATH,$(2))"
CHMOD_EXEC = $(BMN_POSIX_BIN_DIR)chmod +x "$(call NPATH,$(1))"

RSYNC = $(BMN_POSIX_BIN_DIR)rsync
ifeq (,$(BMN_PYTHON_BIN_DIR))
PYTHON = /usr/bin/env python3
else
PYTHON = $(BMN_PYTHON_BIN_DIR)python3
endif
RCC = $(BMN_PYSIDE_BIN_DIR)pyside6-rcc
LUPDATE = $(BMN_PYSIDE_BIN_DIR)pyside6-lupdate
LRELEASE = $(BMN_PYSIDE_BIN_DIR)pyside6-lrelease
MAKENSIS =
DMGBUILD = $(BMN_DMGBUILD_BIN_DIR)dmgbuild
APPIMAGETOOL = $(BMN_APPIMAGE_BIN_DIR)appimagetool
endif

RSYNC_FLAGS = \
    --progress \
    --human-readable \
    --links \
    --chmod=u=rw,go=r \
    --times \
    --stats \

################################################################################
# Version
################################################################################

export BMN_TRANSLATION_LIST := $(sort \
	de_DE \
	fr_FR \
	ja_JP \
	ru_RU \
	zh_CN \
)

define BMN_VERSION
$(strip $(shell $(PYTHON) -c \
'from $(BMN_PACKAGE_NAME) import version;\
print(str(version.$(1)))\
'))
endef

define FILE_MTIME
$(strip $(shell $(PYTHON) -c \
'import datetime;import os;\
mtime=os.stat("$(1)").st_mtime if os.path.exists("$(1)") else 0;\
mtime=datetime.datetime.utcfromtimestamp(mtime);\
print(mtime.strftime("%y%m%d_%H%M%S"))\
'))
endef

export BMN_PACKAGE_NAME = bmnclient
export BMN_UPLOAD_DIR = bmn-upload:public/$(PLATFORM)

$(info Loading version from ${BMN_PACKAGE_NAME} package...)
export BMN_MAINTAINER := $(or $(strip \
	$(call BMN_VERSION,Product.MAINTAINER)),\
	$(error BMN_MAINTAINER not defined.))
export BMN_MAINTAINER_DOMAIN := $(or $(strip \
	$(call BMN_VERSION,Product.MAINTAINER_DOMAIN)),\
	$(error BMN_MAINTAINER_DOMAIN not defined.))
export BMN_MAINTAINER_URL := $(or $(strip \
	$(call BMN_VERSION,Product.MAINTAINER_URL)),\
	$(error BMN_MAINTAINER_URL not defined.))
export BMN_NAME := $(or $(strip \
	$(call BMN_VERSION,Product.NAME)),\
	$(error BMN_NAME not defined.))
export BMN_SHORT_NAME := $(or $(strip \
	$(call BMN_VERSION,Product.SHORT_NAME)),\
	$(error BMN_SHORT_NAME not defined.))
export BMN_VERSION_STRING := $(or $(strip \
	$(call BMN_VERSION,Product.VERSION_STRING)),\
	$(error BMN_VERSION_STRING not defined.))
export BMN_ICON_WINDOWS_FILE_PATH := $(or $(strip \
	$(call BMN_VERSION,ProductPaths.ICON_WINDOWS_FILE_PATH)),\
	$(error BMN_ICON_WINDOWS_FILE_PATH not defined.))
export BMN_ICON_DARWIN_FILE_PATH := $(or $(strip \
	$(call BMN_VERSION,ProductPaths.ICON_DARWIN_FILE_PATH)),\
	$(error BMN_ICON_DARWIN_FILE_PATH not defined.))
export BMN_ICON_LINUX_FILE_PATH := $(or $(strip \
	$(call BMN_VERSION,ProductPaths.ICON_LINUX_FILE_PATH)),\
	$(error BMN_ICON_LINUX_FILE_PATH not defined.))

TARGET_SUFFIX_RELEASE =
TARGET_SUFFIX_DEBUG = _debug

export TARGET_NAME_RELEASE = \
	$(BMN_SHORT_NAME)$(TARGET_SUFFIX_RELEASE)$(EXEC_SUFFIX)
export TARGET_NAME_DEBUG = \
	$(BMN_SHORT_NAME)$(TARGET_SUFFIX_DEBUG)$(EXEC_SUFFIX)

################################################################################
# Utils
################################################################################

# https://blog.jgc.org/2011/07/gnu-make-recursive-wildcard-function.html
RWILDCARD = $(foreach d,$(wildcard $(1)*),$(call RWILDCARD,$(d)/,$(2))$(filter $(subst *,%,$(2)),$(d)))

# new line char
define NL


endef

################################################################################
# Common directories
################################################################################

#export BASE_DIR := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
export BASE_DIR = .
export CONTRIB_DIR = $(BASE_DIR)/contrib
export CONTRIB_PLATFORM_DIR = $(CONTRIB_DIR)/$(PLATFORM)
export PACKAGE_DIR = $(BASE_DIR)/$(BMN_PACKAGE_NAME)
export RESOURCES_DIR = $(PACKAGE_DIR)/resources
export TRANSLATIONS_DIR = $(RESOURCES_DIR)/translations
export TESTS_DIR = $(BASE_DIR)/tests

# DON'T CHANGE! setuptools paths
export DIST_DIR = $(BASE_DIR)/dist
export BUILD_DIR = $(BASE_DIR)/build

################################################################################
# Sources
################################################################################

PY_SOURCES := $(sort $(call RWILDCARD,$(PACKAGE_DIR)/,*.py))
QML_SOURCES := $(sort $(call RWILDCARD,$(RESOURCES_DIR)/,*.qml))

################################################################################
# QRC
################################################################################

export USE_QRC ?= 0

QRC_SOURCES := $(sort $(call RWILDCARD,$(RESOURCES_DIR)/,*.qml *.svg *qmldir))
QRC_SOURCE = $(BUILD_DIR)/resources.qrc
QRC_TARGET = $(RESOURCES_DIR)/qrc/__init__.py

PY_SOURCES := $(filter-out $(QRC_TARGET),$(PY_SOURCES))

QRC_PUT = $(file >>$(2),<file alias="$(patsubst $(RESOURCES_DIR)/%,%,$(1))">$(call NPATH,$(abspath $(1)))</file>)
QRC_PUT_TR = $(file >>$(2),<file alias="$(patsubst $(RESOURCES_DIR)/%,%,$(1))">$(call NPATH,$(abspath $(1)))</file>)

################################################################################
# Translations
################################################################################

TR_SOURCES := $(addprefix $(TRANSLATIONS_DIR)/,$(addsuffix .ts,$(BMN_TRANSLATION_LIST)))
TR_OBJECTS := $(addprefix $(TRANSLATIONS_DIR)/,$(patsubst %.ts,%.qm,$(notdir $(TR_SOURCES))))

################################################################################
# PyInstaller
#################################################################################

PYINSTALLER_WORK_DIR = $(BUILD_DIR)/pyinstaller

################################################################################
# PIP
################################################################################

PIP_DIST_TARGET_PREFIX := $(DIST_DIR)/$(BMN_PACKAGE_NAME)-$(BMN_VERSION_STRING)
PIP_DIST_TARGET_WHEEL := $(PIP_DIST_TARGET_PREFIX)-py3-none-any.whl
PIP_DIST_TARGET_SDIST := $(PIP_DIST_TARGET_PREFIX).tar.gz

################################################################################
# Targets
################################################################################

.PHONY: all
all: tr qrc

.PHONY: clean
clean: check-clean tr-mostlyclean qrc-clean pip-clean dist-clean

################################################################################

.PHONY: gui gui-debug
gui: all
	$(PYTHON) -m $(BMN_PACKAGE_NAME)
gui-debug: all
	$(PYTHON) -m $(BMN_PACKAGE_NAME) -d

.PHONY: check
check: T = $(call NPATH,$(BASE_DIR))
check: S = $(call NPATH,$(TESTS_DIR))
check: all
	$(PYTHON) -m tox || $(PYTHON) -m unittest discover -t "$(T)" -s "$(S)" -v


.PHONY: check-clean
check-clean:
	$(call RMDIR,$(BASE_DIR)/.tox)

################################################################################

.PHONY: tr
tr: $(TR_OBJECTS)

.PHONY: tr-update
tr-update: $(TR_SOURCES)

.PHONY: tr-clean
tr-clean: tr-mostlyclean
	$(foreach F,$(TR_SOURCES),$(call RM,$(F))$(NL))

.PHONY: tr-mostlyclean
tr-mostlyclean:
	$(foreach F,$(TR_OBJECTS),$(call RM,$(F))$(NL))

%.qm: %.ts
	@$(call MKDIR,$(@D))
	$(LRELEASE) -silent -removeidentical "$<" -qm "$(call NPATH,$@)"

$(TR_SOURCES): $(PY_SOURCES) $(QML_SOURCES)
	@$(call MKDIR,$(@D))
	$(LUPDATE) -verbose $(foreach F,$+,"$(call NPATH,${F})") -ts "$(call NPATH,$@)"

################################################################################

.PHONY: qrc
ifeq ($(USE_QRC), 1)
qrc: $(QRC_TARGET)
else
qrc:
endif

.PHONY: qrc-clean
qrc-clean:
	$(call RM,$(QRC_TARGET))
	$(call RM,$(QRC_SOURCE))

$(QRC_TARGET): $(QRC_SOURCE)
	@$(call MKDIR,$(@D))
	$(RCC) "$(call NPATH,$<)" --no-compress -o "$(call NPATH,$@)"

$(QRC_SOURCE)::
	@$(call MKDIR,$(@D))

$(QRC_SOURCE):: $(QRC_SOURCES) $(TR_OBJECTS)
	$(file >$@,<?xml version="1.0"?>)
	$(file >> $@,<RCC><qresource prefix="/">)
	$(foreach F,$(QRC_SOURCES),$(call QRC_PUT,$(F),$@))
	$(foreach F,$(TR_OBJECTS),$(call QRC_PUT_TR,$(F),$@))
	$(file >>$@,</qresource></RCC>)

################################################################################

.PHONY: dist
dist:: all ;

dist::
	$(PYTHON) -m PyInstaller \
		--log-level WARN \
		--clean \
		--noconfirm \
		--distpath "$(call NPATH,$(DIST_DIR))" \
		--workpath "$(call NPATH,$(PYINSTALLER_WORK_DIR))" \
		"$(call NPATH,$(CONTRIB_DIR)/pyinstaller.spec)"

.PHONY: distclean
distclean: dist-clean ;

.PHONY: dist-clean
dist-clean::
	$(call RMDIR,$(PYINSTALLER_WORK_DIR))
	$(call RMDIR,$(DIST_SOURCE_DIR))
	$(call RM,$(DIST_TARGET))
	$(call RM,$(DIST_DIR)/$(BMN_SHORT_NAME).datas)
	$(call RM,$(DIST_DIR)/$(BMN_SHORT_NAME).binaries)
	$(call RM,$(DIST_DIR)/$(BMN_SHORT_NAME).scripts)

include $(CONTRIB_PLATFORM_DIR)/dist.mk

################################################################################

.PHONY: pip-dist
pip-dist: all pip-clean
# DIST_DIR, BUILD_DIR used by default!
	$(PYTHON) ./setup.py sdist
	$(PYTHON) ./setup.py bdist_wheel

.PHONY: pip-clean
pip-clean:
	$(call RMDIR,$(BASE_DIR)/$(BMN_PACKAGE_NAME).egg-info)
	$(call RMDIR,$(BUILD_DIR))
	$(call RM,$(PIP_DIST_TARGET_WHEEL))
	$(call RM,$(PIP_DIST_TARGET_SDIST))

.PHONY: pip-upload
pip-upload:
	$(RSYNC) $(RSYNC_FLAGS) \
		"$(PIP_DIST_TARGET_WHEEL)" \
		"$(PIP_DIST_TARGET_SDIST)" \
		"$(BMN_UPLOAD_DIR)/"

################################################################################

.PHONY: upload
upload: DIST_TARGET_NAME := $(notdir $(DIST_TARGET))
upload: DIST_TARGET_NAME := $(basename $(DIST_TARGET_NAME))-$(call FILE_MTIME,$(DIST_TARGET))$(suffix $(DIST_TARGET_NAME))
upload:
	$(RSYNC) $(RSYNC_FLAGS) \
		"$(DIST_TARGET)" \
		"$(BMN_UPLOAD_DIR)/$(DIST_TARGET_NAME)"
