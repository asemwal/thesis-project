EXEC      = bgpmon
TRANS      = bgpmon_mrt2xml
CC = gcc
CFLAGS = -g -O0 -Wall -fno-strict-aliasing -I.  -I/usr/include/libxml2  -DHAVE_CONFIG_H
LDFLAGS =  -lxml2 -lpthread 

SHELL = /bin/sh

INSTALL = /usr/bin/install -c
INSTALL_PROGRAM = ${INSTALL}
INSTALL_DATA = ${INSTALL} -m 644
INSTALL_MODE= -m 0755
HAVE_LINUX_TCP_H = @HAVE_LINUX_TCP_H@

# Include some boilerplate Gnu makefile definitions.
prefix = /usr/local
exec_prefix = ${prefix}
bindir = ${exec_prefix}/bin
libdir = ${exec_prefix}/lib
infodir = ${datarootdir}/info
includedir = ${prefix}/include
datarootdir = ${prefix}/share
datadir = ${datarootdir}
docdir = $(datadir)/doc/bgpmon
localedir = $(datadir)/locale
mandir = ${datarootdir}/man
manpfx = man
man1ext = .1
man1dir = $(mandir)/$(manpfx)1
man3ext = .3
man3dir = $(mandir)/$(manpfx)3
htmldir = ${docdir}
statedir = /var
sysconfdir = /etc

## help out with installing the run scripts
CHKCONFIG = no
UPDATERC = /usr/sbin/update-rc.d
STARTSTOPD = /sbin/start-stop-daemon
USERADD = /usr/sbin/useradd
ID = /usr/bin/id
MKDIR_P = /bin/mkdir -p
ENABLE_BGPMONUSER = yes
ENABLE_INITSCRIPTS = yes
CHOWN = `which chown`
#linux or bsd check
#the following is a gmake only construct. 
#OS_R:=$(shell uname -s|tr '[A-Z]' '[a-z]')
OS_R = `uname -s`

edit = sed \
       -e 's|@statedir\[@\]|$(statedir)|g' \
       -e 's|@pkgdatadir\[@\]|$(pkgdatadir)|g' \
       -e 's|@prefix\[@\]|$(prefix)|g'\
       -e 's|@USERADD\[@\]|$(USERADD)|g' \
       -e 's|@CHOWN\[@\]|$(CHOWN)|g' \
       -e 's|@ID\[@\]|$(ID)|g' \
       -e 's|@MKDIR_P\[@\]|$(MKDIR_P)|g' \
       -e 's|@CHKCONFIG\[@\]|$(CHKCONFIG)|g' \
       -e 's|@UPDATERC\[@\]|$(UPDATERC)|g' \
       -e 's|@INSTALL_PROGRAM\[@\]|$(INSTALL_PROGRAM)|g' \
       -e 's|@sysconfdir\[@\]|$(sysconfdir)|g' \
       -e 's|@bindir\[@\]|$(bindir)|g' \
       -e 's|@ENABLE_BGPMONUSER\[@\]|$(ENABLE_BGPMONUSER)|g' \
       -e 's|@ENABLE_INITSCRIPTS\[@\]|$(ENABLE_INITSCRIPTS)|g' \
       -e 's|@OS_R\[@\]|$(OS_R)|g' \
       -e 's|@STARTSTOPD\[@\]|$(STARTSTOPD)|g' 
       

OBJECTDIR = ./Obj
MAINOBJS  = $(OBJECTDIR)/main.o $(OBJECTDIR)/bgpmon_formats.o 
TRANSOBJS  = $(OBJECTDIR)/translator.o $(OBJECTDIR)/translator_functions.o $(OBJECTDIR)/xml_gen.o $(OBJECTDIR)/bgp.o $(OBJECTDIR)/bgpmon_formats.o $(OBJECTDIR)/xmlinternal.o $(OBJECTDIR)/xml_help.o $(OBJECTDIR)/log.o $(OBJECTDIR)/bgppacket.o $(OBJECTDIR)/unp.o $(OBJECTDIR)/backlogUtil.o $(OBJECTDIR)/mrtProcessMSG.o $(OBJECTDIR)/mrtProcessTable.o $(OBJECTDIR)/mrtcontrol.o $(OBJECTDIR)/peersession.o $(OBJECTDIR)/utils.o $(OBJECTDIR)/queue.o $(OBJECTDIR)/gen_skip_msg.o $(OBJECTDIR)/address.o $(OBJECTDIR)/configfile.o $(OBJECTDIR)/acl.o $(OBJECTDIR)/mrtinstance.o $(OBJECTDIR)/mrtUtils.o $(OBJECTDIR)/mrtMessage.o $(OBJECTDIR)/peers.o $(OBJECTDIR)/rtable.o $(OBJECTDIR)/bgpfsm.o $(OBJECTDIR)/label.o $(OBJECTDIR)/pacing.o $(OBJECTDIR)/labelutils.o $(OBJECTDIR)/peergroup.o $(OBJECTDIR)/clientscontrol.o $(OBJECTDIR)/myhash.o $(OBJECTDIR)/chains.o $(OBJECTDIR)/periodic.o $(OBJECTDIR)/XMLUtils.o $(OBJECTDIR)/clientinstance.o $(OBJECTDIR)/chaininstance.o $(OBJECTDIR)/xml.o $(OBJECTDIR)/commands.o $(OBJECTDIR)/login.o $(OBJECTDIR)/commandprompt.o $(OBJECTDIR)/acl_commands.o $(OBJECTDIR)/chain_commands.o $(OBJECTDIR)/client_commands.o $(OBJECTDIR)/login_commands.o $(OBJECTDIR)/periodic_commands.o $(OBJECTDIR)/peer_commands.o $(OBJECTDIR)/queue_commands.o $(OBJECTDIR)/mrt_commands.o $(OBJECTDIR)/signals.o $(OBJECTDIR)/geolocation.o
UTILOBJS  = $(OBJECTDIR)/log.o $(OBJECTDIR)/signals.o $(OBJECTDIR)/unp.o $(OBJECTDIR)/acl.o $(OBJECTDIR)/utils.o $(OBJECTDIR)/XMLUtils.o $(OBJECTDIR)/address.o $(OBJECTDIR)/bgp.o $(OBJECTDIR)/backlogUtil.o $(OBJECTDIR)/xml_help.o $(OBJECTDIR)/geolocation.o
QUEUEOBJS = $(OBJECTDIR)/queue.o $(OBJECTDIR)/pacing.o $(OBJECTDIR)/gen_skip_msg.o 
LOGINOBJS    = $(OBJECTDIR)/login.o $(OBJECTDIR)/commandprompt.o $(OBJECTDIR)/commands.o $(OBJECTDIR)/acl_commands.o $(OBJECTDIR)/chain_commands.o $(OBJECTDIR)/client_commands.o $(OBJECTDIR)/login_commands.o $(OBJECTDIR)/periodic_commands.o $(OBJECTDIR)/peer_commands.o $(OBJECTDIR)/queue_commands.o $(OBJECTDIR)/mrt_commands.o
CONFIGOBJS   = $(OBJECTDIR)/configfile.o 
CHAINSOBJS   = $(OBJECTDIR)/chains.o $(OBJECTDIR)/chaininstance.o 
CLIENTSOBJS  = $(OBJECTDIR)/clientscontrol.o $(OBJECTDIR)/clientinstance.o 
LABELOBJS    = $(OBJECTDIR)/label.o $(OBJECTDIR)/myhash.o $(OBJECTDIR)/labelutils.o $(OBJECTDIR)/rtable.o 
PEEROBJS     = $(OBJECTDIR)/bgpfsm.o $(OBJECTDIR)/peersession.o $(OBJECTDIR)/bgppacket.o $(OBJECTDIR)/peers.o $(OBJECTDIR)/peergroup.o
PERIODICOBJS = $(OBJECTDIR)/periodic.o
XMLOBJS      = $(OBJECTDIR)/xmlinternal.o $(OBJECTDIR)/xml.o $(OBJECTDIR)/xml_gen.o
MRTOBJS  = $(OBJECTDIR)/mrtUtils.o $(OBJECTDIR)/mrtcontrol.o $(OBJECTDIR)/mrtProcessTable.o $(OBJECTDIR)/mrtinstance.o $(OBJECTDIR)/mrtProcessMSG.o $(OBJECTDIR)/mrtMessage.o

OBJECTS1 = $(MAINOBJS)  $(UTILOBJS) $(QUEUEOBJS) $(LOGINOBJS) $(CONFIGOBJS) $(CLIENTSOBJS) $(MRTOBJS) $(CHAINSOBJS) $(XMLOBJS) $(PEEROBJS) $(LABELOBJS) $(PERIODICOBJS)

OBJECTS2 =   $(UTILOBJS) $(QUEUEOBJS) $(LOGINOBJS) $(CONFIGOBJS) $(CLIENTSOBJS) $(MRTOBJS) $(CHAINSOBJS) $(XMLOBJS) $(PEEROBJS) $(LABELOBJS) $(PERIODICOBJS)

OBJECTST =  $(OBJECTDIR)/bgpmon_formats.o $(UTILOBJS) $(QUEUEOBJS) $(LOGINOBJS) $(CONFIGOBJS) $(CLIENTSOBJS) $(MRTOBJS) $(CHAINSOBJS) $(XMLOBJS) $(PEEROBJS) $(LABELOBJS) $(PERIODICOBJS) $(OBJECTDIR)/bgp_t.o $(OBJECTDIR)/mrtinstance_t.o $(OBJECTDIR)/backlogUtil_t.o $(OBJECTDIR)/rtable_t.o $(OBJECTDIR)/xml_gen_t.o $(OBJECTDIR)/mrtProcessTable_t.o $(OBJECTDIR)/xml_help_t.o

all: ${OBJECTDIR} $(EXEC) $(TRANS) bgpmon_startup_debian bgpmon_startup_fedora bgpmon_startup_freebsd bgpmon_startup_openbsd startup.sh geodbupdate.sh

${OBJECTDIR}:
	mkdir -p ${OBJECTDIR}
	mkdir -p sbin

$(EXEC): $(OBJECTS1) 
	$(CC) $(CFLAGS) $(OBJECTS1) $(LDFLAGS) -o $(EXEC)

$(TRANS): $(TRANSOBJS)
	$(CC) $(CFLAGS) $(TRANSOBJS) $(LDFLAGS) -o $(TRANS)

$(OBJECTDIR)/translator.o: src/util/translator/translator.c
	$(CC) $(CFLAGS) -c src/util/translator/translator.c -o $(OBJECTDIR)/translator.o

$(OBJECTDIR)/translator_functions.o: src/util/translator/translator_functions.c
	$(CC) $(CFLAGS) -c src/util/translator/translator_functions.c -o $(OBJECTDIR)/translator_functions.o

$(OBJECTDIR)/main.o: main.c
	$(CC) $(CFLAGS) -c main.c -o $(OBJECTDIR)/main.o

$(OBJECTDIR)/geolocation.o: Util/geolocation.c
	$(CC) $(CFLAGS) -c Util/geolocation.c -o $(OBJECTDIR)/geolocation.o

$(OBJECTDIR)/convert.o: Tools/convert.c
	$(CC) $(CFLAGS) -c Tools/convert.c -o $(OBJECTDIR)/convert.o

$(OBJECTDIR)/log.o: Util/log.c
	$(CC) $(CFLAGS) -c Util/log.c -o $(OBJECTDIR)/log.o
	
$(OBJECTDIR)/signals.o: Util/signals.c
	$(CC) $(CFLAGS) -c Util/signals.c -o $(OBJECTDIR)/signals.o

$(OBJECTDIR)/unp.o: Util/unp.c
	$(CC) $(CFLAGS) -c Util/unp.c -o $(OBJECTDIR)/unp.o

$(OBJECTDIR)/acl.o: Util/acl.c
	$(CC) $(CFLAGS) -c Util/acl.c -o $(OBJECTDIR)/acl.o 

$(OBJECTDIR)/utils.o: Util/utils.c
	$(CC) $(CFLAGS) -c Util/utils.c -o $(OBJECTDIR)/utils.o 

$(OBJECTDIR)/backlogUtil.o: Util/backlogUtil.c
	$(CC) $(CFLAGS) -c Util/backlogUtil.c -o $(OBJECTDIR)/backlogUtil.o
	
$(OBJECTDIR)/backlogUtil_t.o: Util/backlogUtil_t.c
	$(CC) $(CFLAGS) -c Util/backlogUtil_t.c -o $(OBJECTDIR)/backlogUtil_t.o
	
$(OBJECTDIR)/queue.o: Queues/queue.c
	$(CC) $(CFLAGS) -c Queues/queue.c -o $(OBJECTDIR)/queue.o

$(OBJECTDIR)/pacing.o: Queues/pacing.c
	$(CC) $(CFLAGS) -c Queues/pacing.c -o $(OBJECTDIR)/pacing.o

$(OBJECTDIR)/gen_skip_msg.o: Queues/gen_skip_msg.c
	$(CC) $(CFLAGS) -c Queues/gen_skip_msg.c -o $(OBJECTDIR)/gen_skip_msg.o

$(OBJECTDIR)/XMLUtils.o: Config/XMLUtils.c
	$(CC) $(CFLAGS) -c Config/XMLUtils.c -o $(OBJECTDIR)/XMLUtils.o

$(OBJECTDIR)/clientscontrol.o: Clients/clientscontrol.c
	$(CC) $(CFLAGS) -c Clients/clientscontrol.c -o $(OBJECTDIR)/clientscontrol.o

$(OBJECTDIR)/clientinstance.o: Clients/clientinstance.c
	$(CC) $(CFLAGS) -c Clients/clientinstance.c -o $(OBJECTDIR)/clientinstance.o

$(OBJECTDIR)/mrtcontrol.o: Mrt/mrtcontrol.c
	$(CC) $(CFLAGS) -c Mrt/mrtcontrol.c -o $(OBJECTDIR)/mrtcontrol.o

$(OBJECTDIR)/mrtUtils.o: Mrt/mrtUtils.c
	$(CC) $(CFLAGS) -c Mrt/mrtUtils.c -o $(OBJECTDIR)/mrtUtils.o

$(OBJECTDIR)/mrtinstance_t.o: Mrt/mrtinstance_t.c
	$(CC) $(CFLAGS) -c Mrt/mrtinstance_t.c -o $(OBJECTDIR)/mrtinstance_t.o
	
$(OBJECTDIR)/mrtinstance.o: Mrt/mrtinstance.c
	$(CC) $(CFLAGS) -c Mrt/mrtinstance.c -o $(OBJECTDIR)/mrtinstance.o

$(OBJECTDIR)/mrtMessage.o: Mrt/mrtMessage.c
	$(CC) $(CFLAGS) -c Mrt/mrtMessage.c -o $(OBJECTDIR)/mrtMessage.o

$(OBJECTDIR)/mrtProcessTable.o: Mrt/mrtProcessTable.c
	$(CC) $(CFLAGS) -c Mrt/mrtProcessTable.c -o $(OBJECTDIR)/mrtProcessTable.o
	
$(OBJECTDIR)/mrtProcessMSG.o: Mrt/mrtProcessMSG.c
	$(CC) $(CFLAGS) -c Mrt/mrtProcessMSG.c -o $(OBJECTDIR)/mrtProcessMSG.o
	
$(OBJECTDIR)/chains.o: Chains/chains.c
	$(CC) $(CFLAGS) -c Chains/chains.c -o $(OBJECTDIR)/chains.o	
	
$(OBJECTDIR)/chaininstance.o: Chains/chaininstance.c
	$(CC) $(CFLAGS) -c Chains/chaininstance.c -o $(OBJECTDIR)/chaininstance.o

$(OBJECTDIR)/periodic.o: PeriodicEvents/periodic.c
	$(CC) $(CFLAGS) -c PeriodicEvents/periodic.c -o $(OBJECTDIR)/periodic.o
	
$(OBJECTDIR)/login.o: Login/login.c
	$(CC) $(CFLAGS) -c Login/login.c -o $(OBJECTDIR)/login.o

$(OBJECTDIR)/commandprompt.o: Login/commandprompt.c
	$(CC) $(CFLAGS) -c Login/commandprompt.c -o $(OBJECTDIR)/commandprompt.o
	
$(OBJECTDIR)/commands.o: Login/commands.c 
	$(CC) $(CFLAGS) -c Login/commands.c -o $(OBJECTDIR)/commands.o

$(OBJECTDIR)/acl_commands.o: Login/acl_commands.c 
	$(CC) $(CFLAGS) -c Login/acl_commands.c -o $(OBJECTDIR)/acl_commands.o
	
$(OBJECTDIR)/client_commands.o: Login/client_commands.c 
	$(CC) $(CFLAGS) -c Login/client_commands.c -o $(OBJECTDIR)/client_commands.o

$(OBJECTDIR)/login_commands.o: Login/login_commands.c 
	$(CC) $(CFLAGS) -c Login/login_commands.c -o $(OBJECTDIR)/login_commands.o

$(OBJECTDIR)/chain_commands.o: Login/chain_commands.c 
	$(CC) $(CFLAGS) -c Login/chain_commands.c -o $(OBJECTDIR)/chain_commands.o

$(OBJECTDIR)/periodic_commands.o: Login/periodic_commands.c 
	$(CC) $(CFLAGS) -c Login/periodic_commands.c -o $(OBJECTDIR)/periodic_commands.o

$(OBJECTDIR)/peer_commands.o: Login/peer_commands.c 
	$(CC) $(CFLAGS) -c Login/peer_commands.c -o $(OBJECTDIR)/peer_commands.o

$(OBJECTDIR)/queue_commands.o: Login/queue_commands.c 
	$(CC) $(CFLAGS) -c Login/queue_commands.c -o $(OBJECTDIR)/queue_commands.o

$(OBJECTDIR)/mrt_commands.o: Login/mrt_commands.c 
	$(CC) $(CFLAGS) -c Login/mrt_commands.c -o $(OBJECTDIR)/mrt_commands.o

$(OBJECTDIR)/configfile.o: Config/configfile.c
	$(CC) $(CFLAGS) -c Config/configfile.c -o $(OBJECTDIR)/configfile.o

$(OBJECTDIR)/label.o: Labeling/label.c
	$(CC) $(CFLAGS) -c Labeling/label.c -o $(OBJECTDIR)/label.o

$(OBJECTDIR)/rtable.o: Labeling/rtable.c
	$(CC) $(CFLAGS) -c Labeling/rtable.c -o $(OBJECTDIR)/rtable.o

$(OBJECTDIR)/rtable_t.o: Labeling/rtable_t.c
	$(CC) $(CFLAGS) -c Labeling/rtable_t.c -o $(OBJECTDIR)/rtable_t.o

$(OBJECTDIR)/ltable.o: Labeling/ltable.c
	$(CC) $(CFLAGS) -c Labeling/ltable.c -o $(OBJECTDIR)/ltable.o

$(OBJECTDIR)/myhash.o: Labeling/myhash.c
	$(CC) $(CFLAGS) -c Labeling/myhash.c -o $(OBJECTDIR)/myhash.o	

$(OBJECTDIR)/labelutils.o: Labeling/labelutils.c
	$(CC) $(CFLAGS) -c Labeling/labelutils.c -o $(OBJECTDIR)/labelutils.o	

$(OBJECTDIR)/bgpfsm.o: Peering/bgpfsm.c
	$(CC) $(CFLAGS) -c Peering/bgpfsm.c -o $(OBJECTDIR)/bgpfsm.o

$(OBJECTDIR)/peersession.o: Peering/peersession.c
	$(CC) $(CFLAGS) -c Peering/peersession.c -o $(OBJECTDIR)/peersession.o
	
$(OBJECTDIR)/bgppacket.o: Util/bgppacket.c
	$(CC) $(CFLAGS) -c Util/bgppacket.c -o $(OBJECTDIR)/bgppacket.o

$(OBJECTDIR)/peers.o: Peering/peers.c
	$(CC) $(CFLAGS) -c Peering/peers.c -o $(OBJECTDIR)/peers.o

$(OBJECTDIR)/peergroup.o: Peering/peergroup.c
	$(CC) $(CFLAGS) -c Peering/peergroup.c -o $(OBJECTDIR)/peergroup.o	

$(OBJECTDIR)/xmlinternal.o: XML/xmlinternal.c
	$(CC) $(CFLAGS) -c XML/xmlinternal.c -o $(OBJECTDIR)/xmlinternal.o	

$(OBJECTDIR)/xml.o: XML/xml.c
	$(CC) $(CFLAGS) -c XML/xml.c -o $(OBJECTDIR)/xml.o	

$(OBJECTDIR)/xml_gen.o: XML/xml_gen.c
	$(CC) $(CFLAGS) -c XML/xml_gen.c -o $(OBJECTDIR)/xml_gen.o	

$(OBJECTDIR)/xml_gen_t.o: XML/xml_gen_t.c
	$(CC) $(CFLAGS) -c XML/xml_gen_t.c -o $(OBJECTDIR)/xml_gen_t.o	

$(OBJECTDIR)/mrtProcessTable_t.o: Mrt/mrtProcessTable_t.c
	$(CC) $(CFLAGS) -c Mrt/mrtProcessTable_t.c -o $(OBJECTDIR)/mrtProcessTable_t.o
	
$(OBJECTDIR)/bgpmon_formats.o: Util/bgpmon_formats.c
	$(CC) $(CFLAGS) -c Util/bgpmon_formats.c -o $(OBJECTDIR)/bgpmon_formats.o

$(OBJECTDIR)/address.o: Util/address.c
	$(CC) $(CFLAGS) -c Util/address.c -o $(OBJECTDIR)/address.o

$(OBJECTDIR)/bgp.o: Util/bgp.c
	$(CC) $(CFLAGS) -c Util/bgp.c -o $(OBJECTDIR)/bgp.o

$(OBJECTDIR)/bgp_t.o: Util/bgp_t.c Util/bgp.c
	$(CC) $(CFLAGS) -c Util/bgp_t.c  -o $(OBJECTDIR)/bgp_t.o 

$(OBJECTDIR)/xml_help.o: Util/xml_help.c 
	$(CC) $(CFLAGS) -c Util/xml_help.c  -o $(OBJECTDIR)/xml_help.o 

$(OBJECTDIR)/xml_help_t.o: Util/xml_help_t.c 
	$(CC) $(CFLAGS) -c Util/xml_help_t.c  -o $(OBJECTDIR)/xml_help_t.o 


test: $(OBJECTST)
	$(CC) -g $(CFLAGS) $(OBJECTST) -o test_driver test_driver.c $(LDFLAGS) -lcunit
	./test_driver

testv: $(OBJECTST)
	$(CC) -g $(CFLAGS) $(OBJECTST) -o test_driver test_driver.c $(LDFLAGS) -lcunit
	valgrind --track-origins=yes --leak-check=full --show-reachable=yes ./test_driver

debugtest: $(OBJECTST)
	$(CC) $(CFLAGS) $(OBJECTST) -o test_driver test_driver.c $(LDFLAGS) -lcunit
	gdb ./test_driver

bgpmon_startup_debian bgpmon_startup_fedora bgpmon_startup_openbsd bgpmon_startup_freebsd: Makefile
	rm -f etc/init.d/$@ etc/init.d/$@.tmp
	test -f etc/init.d/$@.in ; \
	$(edit) etc/init.d/$@.in>etc/init.d/$@.tmp
	chmod +x etc/init.d/$@.tmp
	chmod o-w etc/init.d/$@.tmp
	mv etc/init.d/$@.tmp etc/init.d/$@

startup.sh: Makefile src/startup.sh.in
	rm -f sbin/$@ src/$@.tmp
	test -f src/$@.in ; \
	$(edit) src/$@.in >src/$@.tmp
	chmod +x src/$@.tmp
	chmod o-w src/$@.tmp
	mv src/$@.tmp sbin/$@

geodbupdate.sh: Makefile src/geodbupdate.sh
	rm -f sbin/$@
	cp src/$@ sbin/$@
	chmod +x sbin/$@

bgpmon_startup_debian: etc/init.d/bgpmon_startup_debian.in

bgpmon_startup_fedora: etc/init.d/bgpmon_startup_fedora.in

bgpmon_startup_freebsd: etc/init.d/bgpmon_startup_freebsd.in

bgpmon_startup_openbsd: etc/init.d/bgpmon_startup_openbsd.in

startup.sh: src/startup.sh.in

clean:
	rm -f $(EXEC) $(TRANSOBJS) $(TRANS) $(OBJECTS1) $(OBJECTST) config.log config.status test_driver sbin/startup.sh sbin/geodbupdate.sh
	rm -rf ${OBJECTDIR} sbin

install: all
	-( mkdir -p $(bindir) )
	$(INSTALL_PROGRAM) $(INSTALL_MODE) $(EXEC) $(bindir)/$(EXEC)
	-( mkdir -p $(statedir)/run )
	-( mkdir -p $(docdir) )
	$(INSTALL_PROGRAM) README $(docdir)/README
	-( mkdir -p $(sysconfdir) )
	@ if [ -f "$(sysconfdir)/bgpmon_config.txt" ]; then \
		echo "leaving existing configuration file"; \
	else \
		$(INSTALL_PROGRAM)  -m 644 etc/bgpmon_config.txt  ${sysconfdir}/bgpmon_config.txt; \
	fi
	@ if [ -f "$(sysconfdir)/bgpmon_geodb.txt" ]; then \
		echo "merging local geolocation file"; \
		sbin/geodbupdate.sh; \
		$(INSTALL_PROGRAM)  -m 644 etc/bgpmon_geodb_merged.txt  ${sysconfdir}/bgpmon_geodb.txt; \
		rm -f etc/bgpmon_geodb_merged.txt;\
	else \
		$(INSTALL_PROGRAM)  -m 644 etc/bgpmon_geodb.txt  ${sysconfdir}/bgpmon_geodb.txt; \
	fi
	@echo "if installing on a linux system with capabilities enabled and want bgpmon to bind on a priviledged port (179) run:sudo setcap 'cap_net_bind_service=+ep' /usr/local/bin/bgpmon";
	sbin/startup.sh
