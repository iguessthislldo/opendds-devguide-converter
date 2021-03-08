######################
Run-time Configuration
######################

**********************
Configuration Approach
**********************

OpenDDS includes a file-based configuration framework for configuring global options and options related to specific publishers and subscribers such as discovery and transport configuration.
OpenDDS also allows configuration via the command line for a limited number of options and via a configuration API.
This chapter summarizes the configuration options supported by OpenDDS.

OpenDDS configuration is concerned with three main areas:

* **Common Configuration Options** – configure the behavior of DCPS entities at a global level.
  This allows separately deployed processes in a computing environment to share common settings for the specified behavior (e.g.
  all readers and writers should use RTPS discovery).

* **Discovery Configuration Options** – configure the behavior of the discovery mechanism(s).
  OpenDDS supports multiple approaches for discovering and associating writers and readers as detailed in Section :ref:`Discovery Configuration`.

* **Transport Configuration Options** – configure the Extensible Transport Framework (ETF) which abstracts the transport layer from the DCPS layer of OpenDDS.
  Each pluggable transport can be configured separately.

The configuration file for OpenDDS is a human-readable ini-style text file.
Table 7-1 shows a list of the available configuration section types as they relate to the area of OpenDDS that they configure.

**Table 7-1 Configuration File Sections**

+------------------+------------------------+
| **Focus Area**   | **File Section Title** |
+==================+========================+
| Global Settings  | ``[common]``           |
+------------------+------------------------+
| Discovery        | ``[domain]``           |
|                  |                        |
|                  | ``[repository]``       |
|                  |                        |
|                  | ``[rtps_discovery]``   |
+------------------+------------------------+
| Static Discovery | ``[endpoint]``         |
|                  |                        |
|                  | ``[topic]``            |
|                  |                        |
|                  | ``[datawriterqos]``    |
|                  |                        |
|                  | ``[datareaderqos]``    |
|                  |                        |
|                  | ``[publisherqos]``     |
|                  |                        |
|                  | ``[subscriberqos]``    |
+------------------+------------------------+
| Transport        | ``[config]``           |
|                  |                        |
|                  | ``[transport]``        |
+------------------+------------------------+

For each of the section types with the exception of ``[common]``, the syntax of a section header takes the form of ``[section type/instance]``.
For example, a ``[repository]`` section type would always be used in a configuration file like so:

``[repository/repo_1]`` where ``repository`` is the section type and ``repo_1`` is an instance name of a repository configuration.
How to use instances to configure discovery and transports is explained further in Sections :ref:`Discovery Configuration` and :ref:`Transport Configuration`.

The ``-DCPSConfigFile`` command-line argument can be used to pass the location of a configuration file to OpenDDS.
For example:

Windows:

::

        publisher -DCPSConfigFile pub.ini

Unix:

::

        ./publisher -DCPSConfigFile pub.ini

Command-line arguments are passed to the service participant singleton when initializing the domain participant factory.
This is accomplished by using the ``TheParticipantFactoryWithArgs`` macro:

.. code-block:: cpp

    #include <dds/DCPS/Service_Participant.h>

    int main (int argc, char* argv[])
    {

      DDS::DomainParticipantFactory_var dpf =
        TheParticipantFactoryWithArgs(argc, argv);

To set a default configuration file to load, use ``TheServiceParticipant->default_configuration_file(ACE_TCHAR* path)``, like in the following example:

.. code-block:: cpp

    #include <dds/DCPS/Service_Participant.h>

    int main (int argc, char* argv[])
    {

      TheServiceParticipant->default_configuration_file(ACE_TEXT(“pub.ini”));

      DDS::DomainParticipantFactory_var dpf =
        TheParticipantFactoryWithArgs(argc, argv);

``pub.ini would`` be used unless ``-DCPSConfigFile`` is passed to override the default configuration file.

The ``Service_Participant`` class also provides methods that allow an application to configure the DDS service.
See the header file ``$DDS_ROOT/dds/DCPS/Service_Participant.h`` for details.

The following subsections detail each of the configuration file sections and the available options related to those sections.

****************************
Common Configuration Options
****************************

The ``[common]`` section of an OpenDDS configuration file contains options such as the debugging output level, the location of the ``DCPSInfoRepo`` process, and memory preallocation settings.
A sample ``[common]`` section follows:

.. code-block:: ini

        [common]
        DCPSDebugLevel=0
        DCPSInfoRepo=localhost:12345
        DCPSLivelinessFactor=80
        DCPSChunks=20
        DCPSChunksAssociationMultiplier=10
        DCPSBitLookupDurationMsec=2000
        DCPSPendingTimeout=30


It is not necessary to specify every option.

Option values in the ``[common]`` section with names that begin with “``DCPS``” can be overridden by a command-line argument.
The command-line argument has the same name as the configuration option with a “``-``” prepended to it.
For example:

::

        subscriber -DCPSInfoRepo localhost:12345

The following table summarizes the ``[common]`` configuration options:

**Table 7-2 Common Configuration Options**

+-----------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------+
| Option                                        | Description                                                                                                                                                                                                                            | Default                                                           |
+===============================================+========================================================================================================================================================================================================================================+===================================================================+
| ``DCPSBit=[1|0]``                             | Toggle Built-In-Topic support.                                                                                                                                                                                                         | ``1``                                                             |
+-----------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------+
| ``DCPSBitLookupDurationMsec=msec``            | The maximum duration in milliseconds that the framework will wait for latent Built-In Topic information when retrieving BIT data given an instance handle.                                                                             | ``2000``                                                          |
|                                               | The participant code may get an instance handle for a remote entity before the framework receives and processes the related BIT information.                                                                                           |                                                                   |
|                                               | The framework waits for up to the given amount of time before it fails the operation.                                                                                                                                                  |                                                                   |
+-----------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------+
| ``DCPSBitTransportIPAddress=addr``            | IP address identifying the local interface to be used by tcp transport for the Built-In Topics.                                                                                                                                        | ``INADDR_ANY``                                                    |
|                                               |                                                                                                                                                                                                                                        |                                                                   |
|                                               | **NOTE**: This property is only applicable to a ``DCPSInfoRepo`` configuration.                                                                                                                                                        |                                                                   |
+-----------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------+
| ``DCPSBitTransportPort=port``                 | Port used by the tcp transport for Built-In Topics.If the default of ‘0’ is used, the operating system will choose a port to use.                                                                                                      | ``0``                                                             |
|                                               | **NOTE**: This property is only applicable to a ``DCPSInfoRepo`` configuration.                                                                                                                                                        |                                                                   |
+-----------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------+
| ``DCPSChunks=n``                              | Configurable number of chunks that a data writer's and reader's cached allocators will preallocate when the ``RESOURCE_LIMITS`` QoS value is infinite.                                                                                 | ``20``                                                            |
|                                               | When all of the preallocated chunks are in use, OpenDDS allocates from the heap.                                                                                                                                                       |                                                                   |
+-----------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------+
| ``DCPSChunkAssociationMultiplier=n``          | Multiplier for the DCPSChunks or ``resource_limits.max_samples`` value to determine the total number of shallow copy chunks that are preallocated.                                                                                     | ``10``                                                            |
|                                               | Set this to a value greater than the number of connections so the preallocated chunk handles do not run out.                                                                                                                           |                                                                   |
|                                               | A sample written to multiple data readers will not be copied multiple times but there is a shallow copy handle to that sample used to manage the delivery to each data reader.                                                         |                                                                   |
|                                               | The size of the handle is small so there is not great need to set this value close to the number of connections.                                                                                                                       |                                                                   |
+-----------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------+
| ``DCPSDebugLevel=n``                          | Integer value that controls the amount of debug information the DCPS layer prints.                                                                                                                                                     | 0                                                                 |
|                                               | Valid values are 0 through 10.                                                                                                                                                                                                         |                                                                   |
+-----------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------+
| ``DCPSDefaultAddress=addr``                   | Default value for the host portion of ``local_address`` for transport instances containing a ``local_address``.                                                                                                                        |                                                                   |
|                                               | Only applied when ``DCPSDefaultAddress`` is set to a non-empty value and no ``local_address`` is specified in the transport.                                                                                                           |                                                                   |
|                                               |                                                                                                                                                                                                                                        |                                                                   |
|                                               | Other subsystems (such as DDSI-RTPS Discovery) use ``DCPSDefaultAddress`` as a default value as well.                                                                                                                                  |                                                                   |
+-----------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------+
| ``DCPSDefaultDiscovery=[``                    | Specifies a discovery configuration to use for any domain not explicitly configured.                                                                                                                                                   | ``DEFAULT_REPO``                                                  |
|                                               | ``DEFAULT_REPO`` translates to using the ``DCPSInfoRepo``.                                                                                                                                                                             |                                                                   |
| ``DEFAULT_REPO|``                             | ``DEFAULT_RTPS`` specifies the use of RTPS for discovery.                                                                                                                                                                              |                                                                   |
|                                               | ``DEFAULT_STATIC`` specifies the use of static discovery.                                                                                                                                                                              |                                                                   |
| ``DEFAULT_RTPS|``                             | See Section :ref:`Discovery Configuration` for details about configuring discovery.                                                                                                                                                    |                                                                   |
|                                               |                                                                                                                                                                                                                                        |                                                                   |
| ``DEFAULT_STATIC|``                           |                                                                                                                                                                                                                                        |                                                                   |
|                                               |                                                                                                                                                                                                                                        |                                                                   |
| ``user-defined configuration instance name]`` |                                                                                                                                                                                                                                        |                                                                   |
+-----------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------+
| ``DCPSGlobalTransportConfig=name``            | Specifies the name of the transport configuration that should be used as the global configuration.                                                                                                                                     | The default configuration is used as described in :ref:`Overview` |
|                                               | This configuration is used by all entities that do not otherwise specify a transport configuration.                                                                                                                                    |                                                                   |
|                                               | A special value of $file uses a transport configuration that includes all transport instances defined in the configuration file.                                                                                                       |                                                                   |
+-----------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------+
| ``DCPSInfoRepo=objref``                       | Object reference for locating the DCPS Information Repository.                                                                                                                                                                         | ``file://repo.ior``                                               |
|                                               | This can either be a full CORBA IOR or a simple host:port string.                                                                                                                                                                      |                                                                   |
+-----------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------+
| ``DCPSLivelinessFactor=n``                    | Percent of the liveliness lease duration after which a liveliness message is sent.                                                                                                                                                     | ``80``                                                            |
|                                               | A value of 80 implies a 20% cushion of latency from the last detected heartbeat message.                                                                                                                                               |                                                                   |
+-----------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------+
| ``DCPSMonitor=[0|1]``                         | Use the OpenDDS_monitor library to publish data on monitoring topics (see dds/monitor/README).                                                                                                                                         | ``0``                                                             |
+-----------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------+
| ``DCPSPendingTimeout=sec``                    | The maximum duration in seconds a data writer will block to allow unsent samples to drain on deletion.                                                                                                                                 | ``0``                                                             |
|                                               | By default, this option blocks indefinitely.                                                                                                                                                                                           |                                                                   |
+-----------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------+
| ``DCPSPersistentDataDir=path``                | The path on the file system where durable data will be stored.                                                                                                                                                                         | ``OpenDDS-durable-data-dir``                                      |
|                                               | If the directory does not exist it will be created automatically.                                                                                                                                                                      |                                                                   |
+-----------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------+
| ``DCPSPublisherContentFilter=[1|0]``          | Controls the filter expression evaluation policy for content filtered topics.                                                                                                                                                          | ``1``                                                             |
|                                               | When enabled (1), the publisher may drop any samples, before handing them off to the transport when these samples would have been ignored by all subscribers.                                                                          |                                                                   |
+-----------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------+
| ``DCPSSecurity=[0|1]``                        | This setting is only available when OpenDDS is compiled with DDS Security enabled.                                                                                                                                                     | ``0``                                                             |
|                                               | If set to 1, enable DDS Security framework and built-in plugins.                                                                                                                                                                       |                                                                   |
|                                               | Each Domain Participant using security must be created with certain QoS policy values.                                                                                                                                                 |                                                                   |
|                                               | See chapter :ref:`DDS Security`: DDS Security for more information.                                                                                                                                                                    |                                                                   |
+-----------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------+
| ``DCPSSecurityDebug=CAT[,CAT...]``            | This setting is only available when OpenDDS is compiled with DDS Security enabled.                                                                                                                                                     | ``0``                                                             |
|                                               | This controls the security debug logging granularity by category.                                                                                                                                                                      |                                                                   |
|                                               | See Section 7.6.3 “Security Logging” for details.                                                                                                                                                                                      |                                                                   |
+-----------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------+
| ``DCPSSecurityDebugLevel=n``                  | This setting is only available when OpenDDS is compiled with DDS Security enabled.                                                                                                                                                     | ``N/A``                                                           |
|                                               | This controls the security debug logging granularity by debug level.                                                                                                                                                                   |                                                                   |
|                                               | See Section 7.6.3 “Security Logging” for details.                                                                                                                                                                                      |                                                                   |
+-----------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------+
| ``DCPSSecurityFakeEncryption=[0|1]``          | This setting is only available when OpenDDS is compiled with DDS Security enabled.                                                                                                                                                     | ``0``                                                             |
|                                               | This option, when set to 1, disables all encryption by making encryption and decryption no-ops.                                                                                                                                        |                                                                   |
|                                               | OpenDDS still generates keys and performs other security bookkeeping, so this option is useful for debugging the security infrastructure by making it possible to manually inspect all messages.                                       |                                                                   |
+-----------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------+
| ``pool_size=n_bytes``                         | Size of safety profile memory pool, in bytes.                                                                                                                                                                                          | ``41943040 (40 MiB)``                                             |
+-----------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------+
| ``pool_granularity=n_bytes``                  | Granularity of safety profile memory pool in bytes.                                                                                                                                                                                    | ``8``                                                             |
|                                               | Must be multiple of 8.                                                                                                                                                                                                                 |                                                                   |
+-----------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------+
| ``Scheduler=[``                               | Selects the thread scheduler to use.                                                                                                                                                                                                   | SCHED_OTHER                                                       |
|                                               | Setting the scheduler to a value other than the default requires privileges on most systems.                                                                                                                                           |                                                                   |
| ``SCHED_RR|``                                 | A value of ``SCHED_RR``, ``SCHED_FIFO``, or ``SCHED_OTHER`` can be set.                                                                                                                                                                |                                                                   |
|                                               | ``SCHED_OTHER`` is the default scheduler on most systems; ``SCHED_RR`` is a round robin scheduling algorithm; and ``SCHED_FIFO`` allows each thread to run until it either blocks or completes before switching to a different thread. |                                                                   |
| ``SCHED_FIFO|``                               |                                                                                                                                                                                                                                        |                                                                   |
|                                               |                                                                                                                                                                                                                                        |                                                                   |
| ``SCHED_OTHER]``                              |                                                                                                                                                                                                                                        |                                                                   |
+-----------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------+
| ``scheduler_slice=usec``                      | Some operating systems, such as SunOS, require a time slice value to be set when selecting schedulers other than the default.                                                                                                          | ``none``                                                          |
|                                               | For those systems, this option can be used to set a value in microseconds.                                                                                                                                                             |                                                                   |
+-----------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------+
| ``DCPSBidirGIOP=[0|1]``                       | Use TAO’s BiDirectional GIOP feature for interaction with the DCPSInfoRepo.                                                                                                                                                            | ``1``                                                             |
|                                               | With BiDir enabled, fewer sockets are needed since the same socket can be used for both client and server roles.                                                                                                                       |                                                                   |
+-----------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------+
| ``DCPSThreadStatusInterval=sec``              | Enable internal thread status reporting (see section :ref:`OpenDDSInternalThread Topic`) using the specified reporting interval, in seconds.                                                                                           | ``0 (disabled)``                                                  |
+-----------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------+

The ``DCPSInfoRepo`` option’s value is passed to ``CORBA::ORB::string_to_object()`` and can be any Object URL type understandable by TAO (file, IOR, corbaloc, corbaname).
A simplified endpoint description of the form ``<host>:<port>`` is also accepted.
It is equivalent to ``corbaloc::<host>:<port>/DCPSInfoRepo``.

The ``DCPSChunks`` option allows application developers to tune the amount of memory preallocated when the ``RESOURCE_LIMITS`` are set to infinite.
Once the allocated memory is exhausted, additional chunks are allocated/deallocated from the heap.
This feature of allocating from the heap when the preallocated memory is exhausted provides flexibility but performance will decrease when the preallocated memory is exhausted.

***********************
Discovery Configuration
***********************

In DDS implementations, participants are instantiated in application processes and must discover one another in order to communicate.
A DDS implementation uses the feature of domains to give context to the data being exchanged between DDS participants in the same domain.
When DDS applications are written, participants are assigned to a domain and need to ensure their configuration allows each participant to discover the other participants in the same domain.

OpenDDS offers a centralized discovery mechanism, a peer-to-peer discovery mechanism, and a static discovery mechanism.
The centralized mechanism uses a separate service running a ``DCPSInfoRepo`` process.
The RTPS peer-to-peer mechanism uses the DDSI-RTPS discovery protocol standard to achieve non-centralized discovery.
The static discovery mechanism uses the configuration file to determine which writers and readers should be associated and uses the underlying transport to determine which writers and readers exist.
A number of configuration options exist to meet the deployment needs of DDS applications.
Except for static discovery, each mechanism uses default values if no configuration is supplied either via the command line or configuration file.

The following sections show how to configure the advanced discovery capabilities.
For example, some deployments may need to use multiple ``DCPSInfoRepo`` services or DDSI-RTPS discovery to satisfy interoperability requirements.

Domain Configuration
====================

An OpenDDS configuration file uses the ``[domain]`` section type to configure one or more discovery domains with each domain pointing to a discovery configuration in the same file or a default discovery configuration.
OpenDDS applications can use a centralized discovery approach using the ``DCPSInfoRepo`` service or a peer-to-peer discovery approach using the RTPS discovery protocol standard or a combination of the two in the same deployment.
The section type for the ``DCPSInfoRepo`` method is ``[repository]`` and the section type for an RTPS discovery configuration is ``[rtps_discovery]``.
The static discovery mechanism does not have a dedicated section.
Instead, users are expected to refer to the ``DEFAULT_STATIC`` instance.
A single domain can refer to only one type of discovery section.

See Sections :ref:`Configuring Applications for DCPSInfoRepo` for configuring ``[repository]`` sections, :ref:`Configuring for DDSI-RTPS Discovery` for configuring ``[rtps_discovery]``, and :ref:`Configuring for Static Discovery` for configuring static discovery.

Ultimately a domain is assigned an integer value and a configuration file can support this in two ways.
The first is to simply make the instance value the integer value assigned to the domain as shown here:

.. code-block:: ini

    [domain/1]
    DiscoveryConfig=DiscoveryConfig1
        (more properties...)

Our example configures a single domain identified by the domain keyword and followed by an instance value of ``/1``.
The instance value after the slash in this case is the integer value assigned to the domain.
An alternative syntax for this same content is to use a more recognizable (friendly) name instead of a number for the domain name and then add the ``DomainId`` property to the section to give the integer value.
Here is an example:

.. code-block:: ini

    [domain/books]
    DomainId=1
    DiscoveryConfig=DiscoveryConfig1

The domain is given a friendly name of books.
The ``DomainId`` property assigns the integer value of ``1`` needed by a DDS application reading the configuration.
Multiple domain instances can be identified in a single configuration file in this format.

Once one or more domain instances are established, the discovery properties must be identified for that domain.
The ``DiscoveryConfig`` property must either point to another section that holds the discovery configuration or specify one of the internal default values for discovery (e.g.
``DEFAULT_REPO``, ``DEFAULT_RTPS``, or ``DEFAULT_STATIC``).
The instance name in our example is ``DiscoveryConfig1``.
This instance name must be associated with a section type of either ``[repository]`` or ``[rtps_discovery]``.

Here is an extension of our example:

.. code-block:: ini

    [domain/1]
    DiscoveryConfig=DiscoveryConfig1

    [repository/DiscoveryConfig1]
    RepositoryIor=host1.mydomain.com:12345

In this case our domain points to a ``[repository]`` section which is used for an OpenDDS ``DCPSInfoRepo`` service.
See Section :ref:`Configuring Applications for DCPSInfoRepo` for more details.

There are going to be occasions when specific domains are not identified in the configuration file.
For example, if an OpenDDS application assigns a domain ID of 3 to its participants and the above example does not supply a configuration for domain id of 3 then the following can be used:

.. code-block:: ini

    [common]
    DCPSInfoRepo=host3.mydomain.com:12345
    DCPSDefaultDiscovery=DEFAULT_REPO

    [domain/1]
    DiscoveryConfig=DiscoveryConfig1

    [repository/DiscoveryConfig1]
    RepositoryIor=host1.mydomain.com:12345

The ``DCPSDefaultDiscovery`` property tells the application to assign any participant that doesn’t have a domain id found in the configuration file to use a discovery type of ``DEFAULT_REPO`` which means “use a ``DCPSInfoRepo`` service”  and that ``DCPSInfoRepo`` service can be found at ``host3.mydomain.com:12345``.

As shown in Table 7-2 the ``DCPSDefaultDiscovery`` property has three other values that can be used.
The ``DEFAULT_RTPS`` constant value informs participants that don’t have a domain configuration to use RTPS discovery to find other participants.
Similarly, the ``DEFAULT_STATIC`` constant value informs the participants that don't have a domain configuration to use static discovery to find other participants.

The final option for the ``DCPSDefaultDiscovery`` property is to tell an application to use one of the defined discovery configurations to be the default configuration for any participant domain that isn’t called out in the file.
Here is an example:

.. code-block:: ini

    [common]
    DCPSDefaultDiscovery=DiscoveryConfig2

    [domain/1]
    DiscoveryConfig=DiscoveryConfig1

    [repository/DiscoveryConfig1]
    RepositoryIor=host1.mydomain.com:12345

    [domain/2]
    DiscoveryConfig=DiscoveryConfig2

    [repository/DiscoveryConfig2]
    RepositoryIor=host2.mydomain.com:12345

By adding the ``DCPSDefaultDiscovery`` property to the ``[common]`` section, any participant that hasn’t been assigned to a domain id of ``1`` or ``2`` will use the configuration of ``DiscoveryConfig2``.
For more explanation of a similar configuration for RTPS discovery see Section :ref:`Configuring for DDSI-RTPS Discovery`.

Here are the available properties for the [domain] section.

**Table 7-3 Domain Section Configuration Properties**

+------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Option                                   | Description                                                                                                                                                                                                                                    |
+==========================================+================================================================================================================================================================================================================================================+
| ``DomainId=n``                           | An integer value representing a Domain being associated with a repository.                                                                                                                                                                     |
+------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``DomainRepoKey=k``                      | Key value of the mapped repository                                                                                                                                                                                                             |
|                                          |                                                                                                                                                                                                                                                |
|                                          | (Deprecated.                                                                                                                                                                                                                                   |
|                                          | Provided for backward compatibility).                                                                                                                                                                                                          |
+------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``DiscoveryConfig=config instance name`` | A user-defined string that refers to the instance name of a ``[repository]`` or ``[rtps_discovery]`` section in the same configuration file or one of the internal default values (``DEFAULT_REPO``, ``DEFAULT_RTPS``, or ``DEFAULT_STATIC``). |
|                                          | (Also see the ``DCPSDefaultDiscovery`` property in Table 7-2)                                                                                                                                                                                  |
+------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``DefaultTransportConfig=config``        | A user-defined string that refers to the instance name of a ``[config]`` section.                                                                                                                                                              |
|                                          | See Section :ref:`Transport Configuration`.                                                                                                                                                                                                    |
+------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

Configuring Applications for DCPSInfoRepo
=========================================

An OpenDDS ``DCPSInfoRepo`` is a service on a local or remote node used for participant discovery.
Configuring how participants should find ``DCPSInfoRepo`` is the purpose of this section.
Assume for example that the ``DCPSInfoRepo`` service is started on a host and port of ``myhost.mydomain.com:12345``.
Applications can make their OpenDDS participants aware of how to find this service through command line options or by reading a configuration file.

In our Getting Started example from 2.1.7, “Running the Example” the executables were given a command line parameter to find the ``DCPSInfoRepo`` service like so:

::

    publisher -DCPSInfoRepo file://repo.ior

This assumes that the ``DCPSInfoRepo`` has been started with the following syntax:

Windows:

.. code-block:: doscon

    %DDS_ROOT%\bin\DCPSInfoRepo -o repo.ior

Unix:

.. code-block:: bash

    $DDS_ROOT/bin/DCPSInfoRepo -o repo.ior

The ``DCPSInfoRepo`` service generates its location object information in this file and participants need to read this file to ultimately connect.
The use of file based IORs to find a discovery service, however, is not practical in most production environments, so applications instead can use a command line option like the following to simply point to the host and port where the ``DCPSInfoRepo`` is running.

::

    publisher -DCPSInfoRepo myhost.mydomain.com:12345

The above assumes that the ``DCPSInfoRepo`` has been started on a host (``myhost.mydomain.com``) as follows:

Windows:

.. code-block:: doscon

    %DDS_ROOT%\bin\DCPSInfoRepo -ORBListenEndpoints iiop://:12345

Unix:

.. code-block:: bash

    $DDS_ROOT/bin/DCPSInfoRepo -ORBListenEndpoints iiop://:12345

If an application needs to use a configuration file for other settings, it would become more convenient to place discovery content in the file and reduce command line complexity and clutter.
The use of a configuration file also introduces the opportunity for multiple application processes to share common OpenDDS configuration.
The above example can easily be moved to the ``[common]`` section of a configuration file (assume a file of ``pub.ini``):

.. code-block:: ini

    [common]
    DCPSInfoRepo=myhost.mydomain.com:12345

The command line to start our executable would now change to the following:

::

    publisher -DCSPConfigFile pub.ini

Reinforcing our example from the discussion of domains in section , a configuration file can specify domains with discovery configuration assigned to those domains.
In this case the ``RepositoryIor`` property is used to take the same information that would be supplied on a command line to point to a running ``DCPSInfoRepo`` service.
Two domains are configured here:

.. code-block:: ini

    [domain/1]
    DiscoveryConfig=DiscoveryConfig1

    [repository/DiscoveryConfig1]
    RepositoryIor=myhost.mydomain.com:12345

    [domain/2]
    DiscoveryConfig=DiscoveryConfig2

    [repository/DiscoveryConfig2]
    RepositoryIor=host2.mydomain.com:12345

The ``DiscoveryConfig`` property under ``[domain/1]`` instructs all participants in domain ``1`` to use the configuration defined in an instance called ``DiscoveryConfig1``.
In the above, this is mapped to a ``[repository]`` section that gives the ``RepositoryIor`` value of ``myhost.mydomain.com:12345``.

Finally, when configuring a ``DCPSInfoRepo`` the ``DiscoveryConfig`` property under a domain instance entry can also contain the value of ``DEFAULT_REPO`` which instructs a participant using this instance to use the definition of the property ``DCPSInfoRepo`` wherever it has been supplied.
Consider the following configuration file as an example:

.. code-block:: ini

    [common]
    DCPSInfoRepo=localhost:12345

    [domain/1]
    DiscoveryConfig=DiscoveryConfig1

    [repository/DiscoveryConfig1]
    RepositoryIor=myhost.mydomain.com:12345

    [domain/2]
    DiscoveryConfig=DEFAULT_REPO

In this case any participant in domain 2 would be instructed to refer to the discovery property of ``DCPSInfoRepo``, which is defined in the ``[common]`` section of our example.
If the ``DCPSInfoRepo`` value is not supplied in the ``[common]`` section, it could alternatively be supplied as a parameter to the command line like so:

::

    publisher -DCPSInfoRepo localhost:12345 -DCPSConfigFile pub.ini

This sets the value of ``DCPSInfoRepo`` such that if participants reading the configuration file pub.ini encounters ``DEFAULT_REPO``, there is a value for it.
If ``DCPSInfoRepo`` is not defined in a configuration file or on the command line, then the OpenDDS default value for ``DCPSInfoRepo`` is ``file://repo.ior``.
As mentioned prior, this is not likely to be the most useful in production environments and should lead to setting the value of ``DCPSInfoRepo`` by one of the means described in this section.

Configuring for Multiple DCPSInfoRepo Instances
-----------------------------------------------

The DDS entities in a single OpenDDS process can be associated with multiple DCPS information repositories (``DCPSInfoRepo``).

The repository information and domain associations can be configured using a configuration file, or via application API.
Internal defaults, command line arguments, and configuration file options will work as-is for existing applications that do not want to use multiple ``DCPSInfoRepo`` associations.

Refer to Figure 7-1 as an example of a process that uses multiple ``DCPSInfoRepo`` repositories.
Processes ``A`` and ``B`` are typical application processes that have been configured to communicate with one another and discover one another in ``InfoRepo_1``.
This is a simple use of basic discovery.
However, an additional layer of context has been applied with the use of a specified domain (Domain ``1``).
DDS entities (data readers/data writers) are restricted to communicate to other entities within that same domain.
This provides a useful method of separating traffic when needed by an application.
Processes ``C`` and ``D`` are configured the same way, but operate in Domain ``2`` and use ``InfoRepo_2``.
The challenge comes when you have an application process that needs to use multiple domains and have separate discovery services.
This is Process ``E`` in our example.
It contains two subscribers, one subscribing to publications from ``InfoRepo_1`` and the other subscribing to publications in ``InfoRepo_2``.
What allows this configuration to work can be found in the ``configE.ini`` file.

.. image:: images/10000200000005B3000003DF6D81BBD995FB0660.png

**Figure 7-1 Multiple DCPSInfoRepo Configuration**

We will now look at the configuration file (referred to as ``configE.ini``) to demonstrate how Process ``E`` can communicate to both domains and separate ``DCPSInfoRepo`` services.
For this example we will only show the discovery aspects of the configuration and not show transport content.

.. code-block:: ini

    configE.ini
    [domain/1]
    DiscoveryConfig=DiscoveryConfig1

    [repository/DiscoveryConfig1]
    RepositoryIor=host1.mydomain.com:12345

    [domain/2]
    DiscoveryConfig=DiscoveryConfig2

    [repository/DiscoveryConfig2]
    RepositoryIor=host2.mydomain.com:12345


When Process ``E`` in Figure 7-1 reads in the above configuration it finds the occurrence of multiple domain sections.
As described in Section  each domain has an instance integer and a property of ``DiscoveryConfig`` defined.

For the first domain (``[domain/1]``), the ``DiscoveryConfig`` property is supplied with the user-defined name of ``DiscoveryConfig1`` value.
This property causes the OpenDDS implementation to find a section title of either ``repository`` or ``rtps_discovery`` and an instance name of ``DiscoveryConfig1``.
In our example, a ``[repository/DiscoveryConfig1]`` section title is found and this becomes the discovery configuration for domain instance ``[domain/1]`` (integer value 1).
The section found now tells us that the address of the ``DCPSInfoRepo`` that this domain should use can be found by using the ``RepositoryIor`` property value.
In particular it is ``host1.mydomain.com`` and port ``12345``.
The values of the ``RepositoryIor`` can be a full CORBA IOR or a simple ``host:port`` string.

A second domain section title ``[domain/2]`` is found in this configuration file along with it’s corresponding repository section ``[repository/DiscoveryConfig2]`` that represents the configuration for the second domain of interest and the ``InfoRepo_2`` repository.
There may be any number of repository or domain sections within a single configuration file.

.. note:: Domains not explicitly configured are automatically associated with the default discovery configuration.

.. note:: Individual DCPSInfoRepos can be associated with multiple domains, however domains cannot be shared between multiple DCPSInfoRepos.

Here are the valid properties for a ``[repository]`` section.

**Table 7-4 Multiple repository configuration sections**

+-----------------------+--------------------------------------+
| Option                | Description                          |
+=======================+======================================+
| ``RepositoryIor=ior`` | Repository IOR or host:port.         |
+-----------------------+--------------------------------------+
| ``RepositoryKey=key`` | Unique key value for the repository. |
|                       | (Deprecated.                         |
|                       | Provided for backward compatibility) |
+-----------------------+--------------------------------------+

Configuring for DDSI-RTPS Discovery
===================================

The OMG DDSI-RTPS specification gives the following simple description that forms the basis for the discovery approach used by OpenDDS and the two different protocols used to accomplish the discovery operations.
The excerpt from the OMG DDSI-RTPS specification Section 8.5.1 is as follows:

“The RTPS specification splits up the discovery protocol into two independent protocols:

1.
Participant Discovery Protocol

2.
Endpoint Discovery Protocol

A Participant Discovery Protocol (PDP) specifies how Participants discover each other in the network.
Once two Participants have discovered each other, they exchange information on the Endpoints they contain using an Endpoint Discovery Protocol (EDP).
Apart from this causality relationship, both protocols can be considered independent.”

The configuration options discussed in this section allow a user to specify property values to change the behavior of the Simple Participant Discovery Protocol (SPDP) and/or the Simple Endpoint Discovery Protocol (SEDP) default settings.

DDSI-RTPS can be configured for a single domain or for multiple domains as was done in Section :ref:`Configuring for Multiple DCPSInfoRepo Instances`.

A simple configuration is achieved by specifying a property in the ``[common]`` section of our example configuration file.

.. code-block:: ini

    configE.ini (for RTPS)
    [common]
    DCPSDefaultDiscovery=DEFAULT_RTPS

All default values for DDSI-RTPS discovery are adopted in this form.
A variant of this same basic configuration is to specify a section to hold more specific parameters of RTPS discovery.
The following example uses the ``[common]`` section to point to an instance of an ``[rtps_discovery]`` section followed by an instance name of ``TheRTPSConfig`` which is supplied by the user.

.. code-block:: ini

    [common]
    DCPSDefaultDiscovery=TheRTPSConfig

    [rtps_discovery/TheRTPSConfig]
    ResendPeriod=5

The instance ``[rtps_discovery/TheRTPSConfig]`` is now the location where properties that vary the default DDSI-RTPS settings get specified.
In our example the ``ResendPeriod=5`` entry sets the number of seconds between periodic announcements of available data readers / data writers and to detect the presence of other data readers / data writers on the network.
This would override the default of 30 seconds.

If your OpenDDS deployment uses multiple domains, the following configuration approach combines the use of the ``[domain]`` section title with ``[rtps_discovery]`` to allow a user to specify particular settings by domain.
It might look like this:

.. code-block:: ini

    configE.ini
    [common]
    DCPSDebugLevel=0

    [domain/1]
    DiscoveryConfig=DiscoveryConfig1

    [rtps_discovery/DiscoveryConfig1]
    ResendPeriod=5

    [domain/2]
    DiscoveryConfig=DiscoveryConfig2

    [rtps_discovery/DiscoveryConfig2]
    ResendPeriod=5
    SedpMulticast=0

Some important implementation notes regarding DDSI-RTPS discovery in OpenDDS are as follows:

#. Domain IDs should be between 0 and 231 (inclusive) due to the way UDP ports are assigned to domain IDs.
   In each OpenDDS process, up to 120 domain participants are supported in each domain.

#. OpenDDS's multicast transport (:ref:`IP Multicast Transport Configuration Options`) does not work with RTPS Discovery due to the way GUIDs are assigned (a warning will be issued if this is attempted).

The OMG DDSI-RTPS specification details several properties that can be adjusted from their defaults that influence the behavior of DDSI-RTPS discovery.
Those properties, along with options specific to OpenDDS’s RTPS Discovery implementation, are listed in Table 7-5.

**Table 7-5 RTPS Discovery Configuration Options**

+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| Option                                         | Description                                                                                                                                                     | Default                                  |
+================================================+=================================================================================================================================================================+==========================================+
| ``ResendPeriod=sec``                           | The number of seconds that a process waits between the announcement of participants (see section 8.5.3 in the OMG DDSI-RTPS specification for details).         | ``30``                                   |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``MinResendDelay``                             | The minimum time in milliseconds between participant announcements.                                                                                             | ``100``                                  |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``QuickResendRatio``                           | Tuning parameter that configures local SPDP resends as a fraction of the resend period.                                                                         | ``0.1``                                  |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``LeaseDuration=sec``                          | Sent as part of the participant announcement.                                                                                                                   | ``300``                                  |
|                                                | It tells the peer participants that if they don’t hear from this participant for the specified duration, then this participant can be considered “not alive.”   |                                          |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``PB=port``                                    | Port Base number.                                                                                                                                               | ``7400``                                 |
|                                                | This number sets the starting point for deriving port numbers used for Simple Endpoint Discovery Protocol (SEDP).                                               |                                          |
|                                                | This property is used in conjunction with ``DG``, ``PG``, ``D0`` (or ``DX``), and ``D1`` to construct the necessary Endpoints for RTPS discovery communication. |                                          |
|                                                | (see section 9.6.1.1 in the OMG DDSI-RTPS specification in how these Endpoints are constructed)                                                                 |                                          |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``DG=n``                                       | An integer value representing the Domain Gain.                                                                                                                  | ``250``                                  |
|                                                | This is a multiplier that assists in formulating Multicast or Unicast ports for RTPS.                                                                           |                                          |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``PG=n``                                       | An integer that assists in configuring SPDP Unicast ports and serves as an offset multiplier as participants are assigned addresses using the formula:          | 2                                        |
|                                                |                                                                                                                                                                 |                                          |
|                                                | ``PB + DG * domainId + d1 + PG * participantId``                                                                                                                |                                          |
|                                                |                                                                                                                                                                 |                                          |
|                                                | (see section 9.6.1.1 in the OMG DDSI-RTPS specification in how these Endpoints are constructed)                                                                 |                                          |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``D0=n``                                       | An integer value that assists in providing an offset for calculating an assignable port in SPDP Multicast configurations.                                       | ``0``                                    |
|                                                | The formula used is:                                                                                                                                            |                                          |
|                                                |                                                                                                                                                                 |                                          |
|                                                | PB + DG * domainId + d0                                                                                                                                         |                                          |
|                                                |                                                                                                                                                                 |                                          |
|                                                | (see section 9.6.1.1 in the OMG DDSI-RTPS specification in how these Endpoints are constructed)                                                                 |                                          |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``D1=n``                                       | An integer value that assists in providing an offset for calculating an assignable port in SPDP Unicast configurations.                                         | ``10``                                   |
|                                                | The formula used is:                                                                                                                                            |                                          |
|                                                |                                                                                                                                                                 |                                          |
|                                                | ``PB + DG * domainId + d1 + PG * participantId``                                                                                                                |                                          |
|                                                |                                                                                                                                                                 |                                          |
|                                                | (see section 9.6.1.1 in the OMG DDSI-RTPS specification in how these Endpoints are constructed)                                                                 |                                          |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``SedpMaxMessageSize``                         | Set the maximum SEDP message size.                                                                                                                              | ``65466``                                |
|                                                | The default is the maximum UDP message size.                                                                                                                    |                                          |
|                                                | See max_message_size in table 7-17.                                                                                                                             |                                          |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``SedpMulticast=[0|1]``                        | A boolean value (0 or 1) that determines whether Multicast is used for the SEDP traffic.                                                                        | ``1``                                    |
|                                                | When set to 1, Multicast is used.                                                                                                                               |                                          |
|                                                | When set to zero (0) Unicast for SEDP is used.                                                                                                                  |                                          |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``SedpLocalAddress=addr:port``                 | Configure the transport instance created and used by SEDP to bind to the specified local address and port.                                                      | ``System default address``               |
|                                                | In order to leave the port unspecified, it can be omitted from the setting but the trailing : must be present.                                                  |                                          |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``SpdpLocalAddress=addr[:port]``               | Address of a local interface, which will be used by SPDP to bind to that specific interface.                                                                    | ``DCPSDefaultAddress, or IPADDR_ANY``    |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``DX=n``                                       | An integer value that assists in providing an offset for calculating a port in SEDP Multicast configurations.                                                   | ``2``                                    |
|                                                | The formula used is:                                                                                                                                            |                                          |
|                                                |                                                                                                                                                                 |                                          |
|                                                | ``PB + DG * domainId + dx``                                                                                                                                     |                                          |
|                                                |                                                                                                                                                                 |                                          |
|                                                | This is only valid when ``SedpMulticast=1``.                                                                                                                    |                                          |
|                                                | This is an OpenDDS extension and not part of the OMG DDSI-RTPS specification.                                                                                   |                                          |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``SpdpSendAddrs=``                             | A list (comma or whitespace separated) of host:port pairs used as destinations for SPDP content.                                                                |                                          |
|                                                | This can be a combination of Unicast and Multicast addresses.                                                                                                   |                                          |
| ``[host:port],[host:port]...``                 |                                                                                                                                                                 |                                          |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``MaxSpdpSequenceMsgResetChecks=n``            | Remove a discovered participant after this number of SPDP messages with earlier sequence numbers.                                                               | 3                                        |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``PeriodicDirectedSpdp=[0|1]``                 | A boolean value that determines whether directed SPDP messages are sent to all participants once every resend period.                                           | 0                                        |
|                                                | This setting should be enabled for participants that cannot use multicast to send SPDP announcements, e.g., an RtpsRelay.                                       |                                          |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``UndirectedSpdp=[0|1]``                       | A boolean value that determines whether undirected SPDP messages are sent.                                                                                      | 1                                        |
|                                                | This setting should be disabled for participants that cannot use multicast to send SPDP announcements, e.g., an RtpsRelay.                                      |                                          |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| InteropMulticastOverride=group_address         | A network address specifying the multicast group to be used for SPDP discovery.                                                                                 | ``239.255.0.1``                          |
|                                                | This overrides the interoperability group of the specification.                                                                                                 |                                          |
|                                                | It can be used, for example, to specify use of a routed group address to provide a larger discovery scope.                                                      |                                          |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``TTL=n``                                      | The value of the Time-To-Live (TTL) field of multicast datagrams sent as part of discovery.                                                                     | ``1``                                    |
|                                                | This value specifies the number of hops the datagram will traverse before being discarded by the network.                                                       |                                          |
|                                                | The default value of 1 means that all data is restricted to the local network subnet.                                                                           |                                          |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``MulticastInterface=iface``                   | Specifies the network interface to be used by this discovery instance.                                                                                          | The system default interface is used     |
|                                                | This uses a platform-specific format that identifies the network interface.                                                                                     |                                          |
|                                                | On Linux systems this would be something like eth ``0``.                                                                                                        |                                          |
|                                                |                                                                                                                                                                 |                                          |
|                                                | If this value is not configured, the Common Configuration value ``DCPSDefaultAddress`` is used to set the multicast interface.                                  |                                          |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``GuidInterface=iface``                        | Specifies the network interface to use when determining which local MAC address should appear in a GUID generated by this node.                                 | The system / ACE library default is used |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``SpdpRtpsRelayAddress=host:port``             | Specifies the address of the RtpsRelay for SPDP messages.                                                                                                       |                                          |
|                                                | See section :ref:`The RtpsRelay`.                                                                                                                               |                                          |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``SpdpRtpsRelaySendPeriod=period``             | Specifies the interval between SPDP announcements sent to the RtpsRelay.                                                                                        | 30 seconds                               |
|                                                | See section :ref:`The RtpsRelay`.                                                                                                                               |                                          |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``SedpRtpsRelayAddress=host:port``             | Specifies the address of the RtpsRelay for SEDP messages.                                                                                                       |                                          |
|                                                | See section :ref:`The RtpsRelay`.                                                                                                                               |                                          |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``RtpsRelayOnly=[0|1]``                        | Only send RTPS message to the RtpsRelay (for debugging).                                                                                                        | 0                                        |
|                                                | See section :ref:`The RtpsRelay`.                                                                                                                               |                                          |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``UseRtpsRelay=[0|1]``                         | Send messages to the RtpsRelay.                                                                                                                                 | 0                                        |
|                                                | Messages will only be sent if SpdpRtpsRelayAddress and/or SedpRtpsRelayAddress is set.                                                                          |                                          |
|                                                | See section :ref:`The RtpsRelay`.                                                                                                                               |                                          |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``SpdpStunServerAddress=host:port``            | Specifies the address of the STUN server to use for SPDP when using ICE.                                                                                        |                                          |
|                                                | See section 15.3                                                                                                                                                |                                          |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``SedpStunServerAddress=host:port``            | Specifies the address of the STUN server to use for SEDP when using ICE.                                                                                        |                                          |
|                                                | See section :ref:`Interactive Connectivity Establishment (ICE) for RTPS`.                                                                                       |                                          |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``UseIce=[0|1]``                               | Enable or disable ICE for both SPDP and SEDP.                                                                                                                   | 0                                        |
|                                                | See section :ref:`Interactive Connectivity Establishment (ICE) for RTPS`.                                                                                       |                                          |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``IceTa=milliseconds``                         | Minimum interval between ICE sends.                                                                                                                             | 50ms                                     |
|                                                | See section :ref:`Interactive Connectivity Establishment (ICE) for RTPS`.                                                                                       |                                          |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``IceConnectivityCheckTTL=seconds``            | Maximum duration of connectivity check.                                                                                                                         | 300s                                     |
|                                                | See section :ref:`Interactive Connectivity Establishment (ICE) for RTPS`.                                                                                       |                                          |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``IceChecklistPeriod=seconds``                 | Attempt to cycle through all of the connectivity checks for a candidate in this amount of time.                                                                 | 10                                       |
|                                                | See section :ref:`Interactive Connectivity Establishment (ICE) for RTPS`.                                                                                       |                                          |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``IceIndicationPeriod=seconds``                | Send STUN indications to peers to maintain NAT bindings at this period.                                                                                         | 15                                       |
|                                                | See section :ref:`Interactive Connectivity Establishment (ICE) for RTPS`.                                                                                       |                                          |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``IceNominatedTTL=seconds``                    | Forget a valid candidate if an indication is not received in this amount of time.                                                                               | 300                                      |
|                                                | See section :ref:`Interactive Connectivity Establishment (ICE) for RTPS`.                                                                                       |                                          |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``IceServerReflexiveAddressPeriod=seconds``    | Send a messages to the STUN server at this period.                                                                                                              | 30                                       |
|                                                | See section :ref:`Interactive Connectivity Establishment (ICE) for RTPS`.                                                                                       |                                          |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``IceServerReflexiveIndicationCount=integer``  | Send this many indications before sending a new binding request to the STUN server.                                                                             | 10                                       |
|                                                | See section :ref:`Interactive Connectivity Establishment (ICE) for RTPS`.                                                                                       |                                          |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``IceDeferredTriggeredCheckTTL=seconds``       | Purge deferred checks after this amount of time.                                                                                                                | 300s                                     |
|                                                | See section :ref:`Interactive Connectivity Establishment (ICE) for RTPS`.                                                                                       |                                          |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``IceChangePasswordPeriod=seconds``            | Change the ICE password after this amount of time.                                                                                                              | 300s                                     |
|                                                | See section :ref:`Interactive Connectivity Establishment (ICE) for RTPS`.                                                                                       |                                          |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``MaxAuthTime=seconds``                        | Set the maximum time for authentication with DDS Security.                                                                                                      | 300s                                     |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``AuthResendPeriod=seconds``                   | Resend authentication messages after this amount of time.                                                                                                       | 1s                                       |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``SecureParticipantUserData=[0|1]``            | If DDS Security is enabled, the Participant’s USER_DATA QoS is omitted from unsecured discovery messages.                                                       | ``0``                                    |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``UseXTypes=[0|1]``                            | Enables discovery extensions from the XTypes specification.                                                                                                     | ``1``                                    |
|                                                | Participants exchange top-level type information in endpoint announcements and extended type information using the Type Lookup Service.                         |                                          |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+
| ``TypeLookupServiceReplyTimeout=milliseconds`` | If a request is sent to a peer’s Type Lookup Service (see UseXTypes above), wait up to this duration for a reply.                                               | ``5 seconds``                            |
+------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------+

.. note:: If the environment variable ``OPENDDS_RTPS_DEFAULT_D0`` is set, its value is used as the ``D0`` default value.

Configuring for Static Discovery
================================

Static discovery may be used when a DDS domain has a fixed number of processes and data readers/writers that are all known a priori.
Data readers and writers are collectively known as *endpoints*.
Using only the configuration file, the static discovery mechanism must be able to determine a network address and the QoS settings for each endpoint.
The static discovery mechanism uses this information to determine all potential associations between readers and writers.
A domain participant learns about the existence of an endpoint through hints supplied by the underlying transport.

.. note:: Currently, static discovery can only be used for endpoints using the RTPS UDP transport.

Static discovery introduces the following configuration file sections:  ``[topic/*]``,``[datawriterqos/*]``, ``[datareaderqos/*]``, ``[publisherqos/*]``, ``[subscriberqos/*]``, and ``[endpoint/*]``.
The ``[topic/*]`` (Table 7-6) section is used to introduce a topic.
The ``[datawriterqos/*]`` (Table 7-7), ``[datareaderqos/*]`` (Table 7-8), ``[publisherqos/*]`` (Table 7-9), and ``[subscriberqos/*]`` (Table 7-10) sections are used to describe a QoS of the associated type.
The ``[endpoint/*]`` (Table 7-11) section describes a data reader or writer.

Data reader and writer objects must be identified by the user so that the static discovery mechanism can associate them with the correct ``[endpoint/*]`` section in the configuration file.
This is done by setting the ``user_data`` of the ``DomainParticipantQos`` to an octet sequence of length 6.
The representation of this octet sequence occurs in the ``participant`` value of an ``[endpoint/*]`` section as a string with two hexadecimal digits per octet.
Similarly, the ``user_data`` of the ``DataReaderQos`` or ``DataWriterQos`` must be set to an octet sequence of length 3 corresponding to the ``entity`` value in the ``[endpoint/*]`` section.
For example, suppose the configuration file contains the following:

.. code-block:: ini

    [topic/MyTopic]
    type_name=TestMsg::TestMsg

    [endpoint/MyReader]
    type=reader
    topic=MyTopic
    config=MyConfig
    domain=34
    participant=0123456789ab
    entity=cdef01

    [config/MyConfig]
    transports=MyTransport

    [transport/MyTransport]
    transport_type=rtps_udp
    use_multicast=0
    local_address=1.2.3.4:30000

The corresponding code to configure the ``DomainParticipantQos`` is:

.. code-block:: cpp

    DDS::DomainParticipantQos dp_qos;
    domainParticipantFactory->get_default_participant_qos(dp_qos);
    dp_qos.user_data.value.length(6);
    dp_qos.user_data.value[0] = 0x01;
    dp_qos.user_data.value[1] = 0x23;
    dp_qos.user_data.value[2] = 0x45;
    dp_qos.user_data.value[3] = 0x67;
    dp_qos.user_data.value[4] = 0x89;
    dp_qos.user_data.value[5] = 0xab;

The code to configure the DataReaderQos is similar:

.. code-block:: cpp

    DDS::DataReaderQos qos;
    subscriber->get_default_datareader_qos(qos);
    qos.user_data.value.length(3);
    qos.user_data.value[0] = 0xcd;
    qos.user_data.value[1] = 0xef;
    qos.user_data.value[2] = 0x01;

The domain id, which is 34 in the example, should be passed to the call to ``create_participant``.

In the example, the endpoint configuration for ``MyReader`` references ``MyConfig`` which in turn references ``MyTransport``.
Transport configuration is described in Section :ref:`Transport Configuration`.
The important detail for static discovery is that at least one of the transports contains a known network address (``1.2.3.4:30000``).
An error will be issued if an address cannot be determined for an endpoint.
The static discovery implementation also checks that the QoS of a data reader or data writer object matches the QoS specified in the configuration file.

**Table 7-6 [topic/*] Configuration Options**

+----------------------+------------------------------------------------------------+------------------------------+
| Option               | Description                                                | Default                      |
+======================+============================================================+==============================+
| ``name=string``      | The name of the topic.                                     | ``Instance name of section`` |
+----------------------+------------------------------------------------------------+------------------------------+
| ``type_name=string`` | Identifier which uniquely defines the sample type.         | ``Required``                 |
|                      | This is typically a  CORBA interface repository type name. |                              |
+----------------------+------------------------------------------------------------+------------------------------+

**Table 7-7 [datawriterqos/*] Configuration Options**

+---------------------------------------------------------------------------------+----------------------------------------+----------------+
| Option                                                                          | Description                            | Default        |
+=================================================================================+========================================+================+
| ``durability.kind=[  VOLATILE|TRANSIENT_LOCAL]``                                | See Section :ref:`DURABILITY`.         | See Table 3-5. |
+---------------------------------------------------------------------------------+----------------------------------------+----------------+
| ``deadline.period.sec=[  numeric|DURATION_INFINITE_SEC]``                       | See Section :ref:`DEADLINE`.           | See Table 3-5. |
+---------------------------------------------------------------------------------+----------------------------------------+----------------+
| ``deadline.period.nanosec=[  numeric|DURATION_INFINITE_NANOSEC]``               | See Section :ref:`DEADLINE`.           | See Table 3-5. |
+---------------------------------------------------------------------------------+----------------------------------------+----------------+
| ``latency_budget.duration.sec=[  numeric|DURATION_INFINITE_SEC]``               | See Section :ref:`LATENCY_BUDGET`.     | See Table 3-5. |
+---------------------------------------------------------------------------------+----------------------------------------+----------------+
| ``latency_budget.duration.nanosec=[  numeric|DURATION_INFINITE_NANOSEC]``       | See Section :ref:`LATENCY_BUDGET`.     | See Table 3-5. |
+---------------------------------------------------------------------------------+----------------------------------------+----------------+
| ``liveliness.kind=[  AUTOMATIC|  MANUAL_BY_TOPIC|  MANUAL_BY_PARTICIPANT]``     | See Section :ref:`LIVELINESS`.         | See Table 3-5. |
+---------------------------------------------------------------------------------+----------------------------------------+----------------+
| ``liveliness.lease_duration.sec=[  numeric|DURATION_INFINITE_SEC]``             | See Section :ref:`LIVELINESS`.         | See Table 3-5. |
+---------------------------------------------------------------------------------+----------------------------------------+----------------+
| ``liveliness.lease_duration.nanosec=[  numeric|DURATION_INFINITE_NANOSEC]``     | See Section :ref:`LIVELINESS`.         | See Table 3-5. |
+---------------------------------------------------------------------------------+----------------------------------------+----------------+
| ``reliability.kind=[BEST_EFFORT|RELIABILE]``                                    | See Section :ref:`RELIABILITY`.        | See Table 3-5. |
+---------------------------------------------------------------------------------+----------------------------------------+----------------+
| ``reliability.max_blocking_time.sec=[  numeric|DURATION_INFINITE_SEC]``         | See Section :ref:`RELIABILITY`.        | See Table 3-5. |
+---------------------------------------------------------------------------------+----------------------------------------+----------------+
| ``reliability.max_blocking_time.nanosec=[  numeric|DURATION_INFINITE_NANOSEC]`` | See Section :ref:`RELIABILITY`.        | See Table 3-5. |
+---------------------------------------------------------------------------------+----------------------------------------+----------------+
| ``destination_order.kind=[  BY_SOURCE_TIMESTAMP|  BY_RECEPTION_TIMESTAMP]``     | See Section :ref:`DESTINATION_ORDER`.  | See Table 3-5. |
+---------------------------------------------------------------------------------+----------------------------------------+----------------+
| ``history.kind=[KEEP_LAST|KEEP_ALL]``                                           | See Section :ref:`HISTORY`.            | See Table 3-5. |
+---------------------------------------------------------------------------------+----------------------------------------+----------------+
| ``history.depth=numeric``                                                       | See Section :ref:`HISTORY`.            | See Table 3-5. |
+---------------------------------------------------------------------------------+----------------------------------------+----------------+
| ``resource_limits.max_samples=numeric``                                         | See Section :ref:`RESOURCE_LIMITS`.    | See Table 3-5. |
+---------------------------------------------------------------------------------+----------------------------------------+----------------+
| ``resource_limits.max_instances=numeric``                                       | See Section :ref:`RESOURCE_LIMITS`.    | See Table 3-5. |
+---------------------------------------------------------------------------------+----------------------------------------+----------------+
| ``resource_limits.max_samples_per_instance=  numeric``                          | See Section :ref:`RESOURCE_LIMITS`.    | See Table 3-5. |
+---------------------------------------------------------------------------------+----------------------------------------+----------------+
| ``transport_priority.value=numeric``                                            | See Section :ref:`TRANSPORT_PRIORITY`. | See Table 3-5. |
+---------------------------------------------------------------------------------+----------------------------------------+----------------+
| ``lifespan.duration.sec=[  numeric|DURATION_INFINITE_SEC]``                     | See Section :ref:`LIFESPAN`.           | See Table 3-5. |
+---------------------------------------------------------------------------------+----------------------------------------+----------------+
| ``lifespan.duration.nanosec=[  numeric|DURATION_INFINITE_NANOSEC]``             | See Section :ref:`LIFESPAN`.           | See Table 3-5. |
+---------------------------------------------------------------------------------+----------------------------------------+----------------+
| ``ownership.kind=[SHARED|EXCLUSIVE]``                                           | See Section :ref:`OWNERSHIP`.          | See Table 3-5. |
+---------------------------------------------------------------------------------+----------------------------------------+----------------+
| ``ownership_strength.value=numeric``                                            | See Section :ref:`OWNERSHIP_STRENGTH`. | See Table 3-5. |
+---------------------------------------------------------------------------------+----------------------------------------+----------------+

**Table 7-8 [datareaderqos/*] Configuration Options**

+----------------------------------------------------------------------------------------------------------+-------------------------------------------+----------------+
| Option                                                                                                   | Description                               | Default        |
+==========================================================================================================+===========================================+================+
| ``durability.kind=[  VOLATILE|TRANSIENT_LOCAL]``                                                         | See Section :ref:`DURABILITY`.            | See Table 3-6. |
+----------------------------------------------------------------------------------------------------------+-------------------------------------------+----------------+
| ``deadline.period.sec=[  numeric|DURATION_INFINITE_SEC]``                                                | See Section :ref:`DEADLINE`.              | See Table 3-6. |
+----------------------------------------------------------------------------------------------------------+-------------------------------------------+----------------+
| ``deadline.period.nanosec=[  numeric|DURATION_INFINITE_NANOSEC]``                                        | See Section :ref:`DEADLINE`.              | See Table 3-6. |
+----------------------------------------------------------------------------------------------------------+-------------------------------------------+----------------+
| ``latency_budget.duration.sec=[  numeric|DURATION_INFINITE_SEC]``                                        | See Section :ref:`LATENCY_BUDGET`.        | See Table 3-6. |
+----------------------------------------------------------------------------------------------------------+-------------------------------------------+----------------+
| ``latency_budget.duration.nanosec=[  numeric|DURATION_INFINITE_NANOSEC]``                                | See Section :ref:`LATENCY_BUDGET`.        | See Table 3-6. |
+----------------------------------------------------------------------------------------------------------+-------------------------------------------+----------------+
| ``liveliness.kind=[  AUTOMATIC|  MANUAL_BY_TOPIC|  MANUAL_BY_PARTICIPANT]``                              | See Section :ref:`LIVELINESS`.            | See Table 3-6. |
+----------------------------------------------------------------------------------------------------------+-------------------------------------------+----------------+
| ``liveliness.lease_duration.sec=[  numeric|DURATION_INFINITE_SEC]``                                      | See Section :ref:`LIVELINESS`.            | See Table 3-6. |
+----------------------------------------------------------------------------------------------------------+-------------------------------------------+----------------+
| ``liveliness.lease_duration.nanosec=[  numeric|DURATION_INFINITE_NANOSEC]``                              | See Section :ref:`LIVELINESS`.            | See Table 3-6. |
+----------------------------------------------------------------------------------------------------------+-------------------------------------------+----------------+
| ``reliability.kind=[BEST_EFFORT|RELIABILE]``                                                             | See Section :ref:`RELIABILITY`.           | See Table 3-6. |
+----------------------------------------------------------------------------------------------------------+-------------------------------------------+----------------+
| ``reliability.max_blocking_time.sec=[  numeric|DURATION_INFINITE_SEC]``                                  | See Section :ref:`RELIABILITY`.           | See Table 3-6. |
+----------------------------------------------------------------------------------------------------------+-------------------------------------------+----------------+
| ``reliability.max_blocking_time.nanosec=[  numeric|DURATION_INFINITE_NANOSEC]``                          | See Section :ref:`RELIABILITY`.           | See Table 3-6. |
+----------------------------------------------------------------------------------------------------------+-------------------------------------------+----------------+
| ``destination_order.kind=[  BY_SOURCE_TIMESTAMP|  BY_RECEPTION_TIMESTAMP]``                              | See Section :ref:`DESTINATION_ORDER`.     | See Table 3-6. |
+----------------------------------------------------------------------------------------------------------+-------------------------------------------+----------------+
| ``history.kind=[KEEP_LAST|KEEP_ALL]``                                                                    | See Section :ref:`HISTORY`.               | See Table 3-6. |
+----------------------------------------------------------------------------------------------------------+-------------------------------------------+----------------+
| ``history.depth=numeric``                                                                                | See Section :ref:`HISTORY`.               | See Table 3-6. |
+----------------------------------------------------------------------------------------------------------+-------------------------------------------+----------------+
| ``resource_limits.max_samples=numeric``                                                                  | See Section :ref:`RESOURCE_LIMITS`.       | See Table 3-6. |
+----------------------------------------------------------------------------------------------------------+-------------------------------------------+----------------+
| ``resource_limits.max_instances=numeric``                                                                | See Section :ref:`RESOURCE_LIMITS`.       | See Table 3-6. |
+----------------------------------------------------------------------------------------------------------+-------------------------------------------+----------------+
| ``resource_limits.max_samples_per_instance=  numeric``                                                   | See Section :ref:`RESOURCE_LIMITS`.       | See Table 3-6. |
+----------------------------------------------------------------------------------------------------------+-------------------------------------------+----------------+
| ``time_based_filter.minimum_separation.sec=[  numeric|DURATION_INFINITE_SEC]``                           | See Section :ref:`TIME_BASED_FILTER`.     | See Table 3-6. |
+----------------------------------------------------------------------------------------------------------+-------------------------------------------+----------------+
| ``time_based_filter.minimum_separation.nanosec=[  numeric|DURATION_INFINITE_NANOSEC]``                   | See Section :ref:`TIME_BASED_FILTER`.     | See Table 3-6. |
+----------------------------------------------------------------------------------------------------------+-------------------------------------------+----------------+
| ``reader_data_lifecycle.autopurge_nowriter_samples_delay.sec=[  numeric|DURATION_INFINITE_SEC]``         | See Section :ref:`READER_DATA_LIFECYCLE`. | See Table 3-6. |
+----------------------------------------------------------------------------------------------------------+-------------------------------------------+----------------+
| ``reader_data_lifecycle.autopurge_nowriter_samples_delay.nanosec=[  numeric|DURATION_INFINITE_NANOSEC]`` | See Section :ref:`READER_DATA_LIFECYCLE`. | See Table 3-6. |
+----------------------------------------------------------------------------------------------------------+-------------------------------------------+----------------+
| ``reader_data_lifecycle.autopurge_dispose_samples_delay.sec=[  numeric|DURATION_INFINITE_SEC]``          | See Section :ref:`READER_DATA_LIFECYCLE`. | See Table 3-6. |
+----------------------------------------------------------------------------------------------------------+-------------------------------------------+----------------+
| ``reader_data_lifecycle.autopurge_dispose_samples_delay.nanosec=[  numeric|DURATION_INFINITE_NANOSEC]``  | See Section :ref:`READER_DATA_LIFECYCLE`. | See Table 3-6. |
+----------------------------------------------------------------------------------------------------------+-------------------------------------------+----------------+

**Table 7-9 [publisherqos/*] Configuration Options**

+------------------------------------------------------+----------------------------------+----------------+
| Option                                               | Description                      | Default        |
+======================================================+==================================+================+
| ``presentation.access_scope=[INSTANCE|TOPIC|GROUP]`` | See Section :ref:`PRESENTATION`. | See Table 3-3. |
+------------------------------------------------------+----------------------------------+----------------+
| ``presentation.coherent_access=[true|false]``        | See Section :ref:`PRESENTATION`. | See Table 3-3. |
+------------------------------------------------------+----------------------------------+----------------+
| ``presentation.ordered_access=[true|false]``         | See Section :ref:`PRESENTATION`. | See Table 3-3. |
+------------------------------------------------------+----------------------------------+----------------+
| ``partition.name=name0,name1,...``                   | See Section :ref:`PARTITION`.    | See Table 3-3. |
+------------------------------------------------------+----------------------------------+----------------+

**Table 7-10 [subscriberqos/*] Configuration Options**

+------------------------------------------------------+----------------------------------+----------------+
| Option                                               | Description                      | Default        |
+======================================================+==================================+================+
| ``presentation.access_scope=[INSTANCE|TOPIC|GROUP]`` | See Section :ref:`PRESENTATION`. | See Table 3-4. |
+------------------------------------------------------+----------------------------------+----------------+
| ``presentation.coherent_access=[true|false]``        | See Section :ref:`PRESENTATION`. | See Table 3-4. |
+------------------------------------------------------+----------------------------------+----------------+
| ``presentation.ordered_access=[true|false]``         | See Section :ref:`PRESENTATION`. | See Table 3-4. |
+------------------------------------------------------+----------------------------------+----------------+
| ``partition.name=name0,name1,...``                   | See Section :ref:`PARTITION`.    | See Table 3-4. |
+------------------------------------------------------+----------------------------------+----------------+

**Table 7-11 [endpoint/*] Configuration Options**

+---------------------------+-------------------------------------------------------------------------------------------+----------------+
| Option                    | Description                                                                               | Default        |
+===========================+===========================================================================================+================+
| ``domain=numeric``        | Domain id for endpoint in range 0-231.                                                    | Required       |
|                           | Used to form GUID of endpoint.                                                            |                |
+---------------------------+-------------------------------------------------------------------------------------------+----------------+
| ``participant=hexstring`` | String of 12 hexadecimal digits.                                                          | Required       |
|                           | Used to form GUID of endpoint.                                                            |                |
|                           | All endpoints with the same domain/participant combination should be in the same process. |                |
+---------------------------+-------------------------------------------------------------------------------------------+----------------+
| ``entity=hexstring``      | String of 6 hexadecimal digits.                                                           | Required       |
|                           | Used to form GUID of endpoint.                                                            |                |
|                           | The combination of domain/participant/entity should be unique.                            |                |
+---------------------------+-------------------------------------------------------------------------------------------+----------------+
| ``type=[reader|writer]``  | Determines if the entity is a data reader or data writer.                                 | Required       |
+---------------------------+-------------------------------------------------------------------------------------------+----------------+
| ``topic=name``            | Refers to a ``[topic/*]`` section.                                                        | Required       |
+---------------------------+-------------------------------------------------------------------------------------------+----------------+
| ``datawriterqos=name``    | Refers to a ``[datawriterqos/*]`` section.                                                | See Table 3-5. |
+---------------------------+-------------------------------------------------------------------------------------------+----------------+
| ``datareaderqos=name``    | Refers to a ``[datareaderqos/*]`` section.                                                | See Table 3-6. |
+---------------------------+-------------------------------------------------------------------------------------------+----------------+
| ``publisherqos=name``     | Refers to a ``[publisherqos/*]`` section.                                                 | See Table 3-3. |
+---------------------------+-------------------------------------------------------------------------------------------+----------------+
| ``subscriberqos=name``    | Refers to a ``[subscriberqos/*]`` section.                                                | See Table 3-4. |
+---------------------------+-------------------------------------------------------------------------------------------+----------------+
| ``config``                | Refers to a transport configuration in a ``[config/*]`` section.                          |                |
|                           | This is used to determine a network address for the endpoint.                             |                |
+---------------------------+-------------------------------------------------------------------------------------------+----------------+

***********************
Transport Configuration
***********************

Beginning with OpenDDS 3.0, a new transport configuration design has been implemented.
The basic goals of this design were to:

* Allow simple deployments to ignore transport configuration and deploy using intelligent defaults (with no transport code required in the publisher or subscriber).

* Enable flexible deployment of applications using only configuration files and command line options.

* Allow deployments that mix transports within individual data writers and writers.
  Publishers and subscribers negotiate the appropriate transport implementation to use based on the details of the transport configuration, QoS settings, and network reachability.

* Support a broader range of application deployments in complex networks.

* Support optimized transport development (such as collocated and shared memory transports - note that these are not currently implemented).

* Integrate support for the ``RELIABILITY`` QoS policy with the underlying transport.

* Whenever possible, avoid dependence on the ACE Service Configurator and its configuration files.

Unfortunately, implementing these new capabilities involved breaking of backward compatibility with OpenDDS transport configuration code and files from previous releases.
See ``$DDS_ROOT/docs/OpenDDS_3.0_Transition.txt`` for information on how to convert your existing application to use the new transport configuration design.

Overview
========

Transport Concepts
------------------

This section provides an overview of the concepts involved in transport configuration and how they interact.

Each data reader and writer uses a *Transport Configuration* consisting of an ordered set of *Transport Instances*.
Each Transport Instance specifies a Transport Implementation (i.e.
tcp, udp, multicast, shmem, or rtps_udp) and can customize the configuration parameters defined by that transport.
Transport Configurations and Transport Instances are managed by the *Transport Registry* and can be created via configuration files or through programming APIs.

Transport Configurations can be specified for Domain Participants, Publishers, Subscribers, Data Writers, and Data Readers.
When a Data Reader or Writer is enabled, it uses the most specific configuration it can locate, either directly bound to it or accessible through its parent entity.
For example, if a Data Writer specifies a Transport Configuration, it always uses it.
If the Data Writer does not specify a configuration, it tries to use that of its Publisher or Domain Participant in that order.
If none of these entities have a transport configuration specified, the *Global Transport Configuration* is obtained from the Transport Registry.
The Global Transport Configuration can be specified by the user via either configuration file, command line option, or a member function call on the Transport Registry.
If not defined by the user, a default transport configuration is used which contains all available transport implementations with their default configuration parameters.
If you don’t specifically load or link in any other transport implementations, OpenDDS uses the tcp transport for all communication.

How OpenDDS Selects a Transport
-------------------------------

Currently, the behavior for OpenDDS is that Data Writers actively connect to Data Readers, which are passively awaiting those connections.
Data Readers “listen” for connections on each of the Transport Instances that are defined in their Transport Configuration.
Data Writers use their Transport Instances to “connect” to those of the Data Readers.
Because the logical connections discussed here don’t correspond to the physical connections of the transport, OpenDDS often refers to them as *Data Links*.

When a Data Writer tries to connect to a Data Reader, it first attempts to see if there is an existing data link that it can use to communicate with that Data Reader.
The Data Writer iterates (in definition order) through each of its Transport Instances and looks for an existing data link to the Transport Instances that the reader defined.
If an existing data link is found it is used for all subsequent communication between the Data Writer and Reader.

If no existing data link is found, the Data Writer attempts to connect using the different Transport Instances in the order they are defined in its Transport Configuration.
Any Transport Instances not “matched” by the other side are skipped.
For example, if the writer specifies udp and tcp transport instances and the reader only specifies tcp, the udp transport instance is ignored.
Matching algorithms may also be affected by QoS parameters, configuration of the instances, and other specifics of the transport implementation.
The first pair of Transport Instances that successfully “connect” results in a data link that is used for all subsequent data sample publication.

Configuration File Examples
===========================

The following examples explain the basic features of transport configuration via files and describe some common use cases.
These are followed by full reference documentation for these features.

Single Transport Configuration
------------------------------

The simplest way to provide a transport configuration for your application is to use the OpenDDS configuration file.
Here is a sample configuration file that might be used by an application running on a computer with two network interfaces that only wants to communicate using one of them:

.. code-block:: ini

    [common]
    DCPSGlobalTransportConfig=myconfig

    [config/myconfig]
    transports=mytcp

    [transport/mytcp]
    transport_type=tcp
    local_address=myhost

This file does the following (starting from the bottom up):

* Defines a transport instance named ``mytcp`` with a transport type of tcp and the local address specified as ``myhost``, which is the host name corresponding to the network interface we want to use.

* Defines a transport configuration named ``myconfig`` that uses the transport instance ``mytcp`` as its only transport.

* Makes the transport configuration named ``myconfig`` the global transport configuration for all entities in this process.

A process using this configuration file utilizes our customized transport configuration for all Data Readers and Writers created by it (unless we specifically bind another configuration in the code as described in :ref:`Using Multiple Configurations`).

Using Mixed Transports
----------------------

This example configures an application to primarily use multicast and to “fall back” to tcp when it is unable to use multicast.
Here is the configuration file:

.. code-block:: ini

    [common]
    DCPSGlobalTransportConfig=myconfig

    [config/myconfig]
    transports=mymulticast,mytcp

    [transport/mymulticast]
    transport_type=multicast

    [transport/mytcp]
    transport_type=tcp

The transport configuration named ``myconfig`` now includes two transport instances, ``mymulticast`` and ``mytcp``.
Neither of these transport instances specify any parameters besides transport_type, so they use the default configuration of these transport implementations.
Users are free to use any of the transport-specific configuration parameters that are listed in the following reference sections.

Assuming that all participating processes use this configuration file, the application attempts to use multicast to initiate communication between data writers and readers.
If the initial multicast communication fails for any reason (possibly because an intervening router is not passing multicast traffic) tcp is used to initiate the connection.

Using Multiple Configurations
-----------------------------

For many applications, one configuration is not equally applicable to all communication within a given process.
These applications must create multiple Transport Configurations and then assign them to the different entities of the process.

For this example consider an application hosted on a computer with two network interfaces that requires communication of some data over one interface and the remainder over the other interface.
Here is our configuration file:

.. code-block:: ini

    [common]
    DCPSGlobalTransportConfig=config_a

    [config/config_a]
    transports=tcp_a

    [config/config_b]
    transports=tcp_b

    [transport/tcp_a]
    transport_type=tcp
    local_address=hosta

    [transport/tcp_b]
    transport_type=tcp
    local_address=hostb

Assuming ``hosta`` and ``hostb`` are the host names assigned to the two network interfaces, we now have separate configurations that can use tcp on the respective networks.
The above file sets the “``A``” side configuration as the default, meaning we must manually bind any entities we want to use the other side to the “``B``” side configuration.

OpenDDS provides two mechanisms to assign configurations to entities:

* Via source code by attaching a configuration to an entity (reader, writer, publisher, subscriber, or domain participant)

* Via configuration file by associating a configuration with a domain

Here is the source code mechanism (using a domain participant):

.. code-block:: cpp

      DDS::DomainParticipant_var dp =
              dpf->create_participant(MY_DOMAIN,
                                      PARTICIPANT_QOS_DEFAULT,
                                      DDS::DomainParticipantListener::_nil(),
                                      OpenDDS::DCPS::DEFAULT_STATUS_MASK);

     OpenDDS::DCPS::TransportRegistry::instance()->bind_config("config_b", dp);

Any Data Writers or Readers owned by this Domain Participant should now use the “``B``” side configuration.

.. note:: When directly binding a configuration to a data writer or reader, the ``bind_config`` call must occur before the reader or writer is enabled.
  This is not an issue when binding configurations to Domain Participants, Publishers, or Subscribers.
  See Section :ref:`ENTITY_FACTORY` for details on how to create entities that are not enabled.

Transport Registry Example
==========================

OpenDDS allows developers to also define transport configurations and instances via C++ APIs.
The ``OpenDDS::DCPS::TransportRegistry`` class is used to construct ``OpenDDS::DCPS::TransportConfig`` and ``OpenDDS::DCPS::TransportInst`` objects.
The ``TransportConfig`` and ``TransportInst`` classes contain public data member corresponding to the options defined below.
This section contains the code equivalent of the simple transport configuration file described in .
First, we need to include the correct header files:

.. code-block:: cpp

    #include <dds/DCPS/transport/framework/TransportRegistry.h>
    #include <dds/DCPS/transport/framework/TransportConfig.h>
    #include <dds/DCPS/transport/framework/TransportInst.h>
    #include <dds/DCPS/transport/tcp/TcpInst.h>

    using namespace OpenDDS::DCPS;

Next we create the transport configuration, create the transport instance, configure the transport instance, and then add the instance to the configuration’s collection of instances:

.. code-block:: cpp

      TransportConfig_rch cfg = TheTransportRegistry->create_config("myconfig");
      TransportInst_rch inst = TheTransportRegistry->create_inst("mytcp", // name
                                                                 "tcp");  // type

      // Must cast to TcpInst to get access to transport-specific options
      TcpInst_rch tcp_inst = dynamic_rchandle_cast<TcpInst>(inst);
      tcp_inst->local_address_str_ = "myhost";

      // Add the inst to the config
      cfg->instances_.push_back(inst);

Lastly, we can make our newly defined transport configuration the global transport configuration:

.. code-block:: cpp

      TheTransportRegistry->global_config(cfg);

This code should be executed before any Data Readers or Writers are enabled.

See the header files included above for the full list of public data members and member functions that can be used.
See the option descriptions in the following sections for a full understanding of the semantics of these settings.

Stepping back and comparing this code to the original configuration file from , the configuration file is much simpler than the corresponding C++ code and has the added advantage of being modifiable at run-time.
It is easy to see why we recommend that almost all applications should use the configuration file mechanism for transport configuration.

Transport Configuration Options
===============================

Transport Configurations are specified in the OpenDDS configuration file via sections with the format of ``[config/<name>]``, where ``<name>`` is a unique name for that configuration within that process.
The following table summarizes the options when specifying a transport configuration:

**Table 7-12 Transport Configuration Options**

+------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------+
| Option                             | Description                                                                                                                                                | Default   |
+====================================+============================================================================================================================================================+===========+
| ``Transports=inst1[,inst2][,...]`` | The ordered list of transport instance names that this configuration will utilize.                                                                         | none      |
|                                    | This field is required for every transport configuration.                                                                                                  |           |
+------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------+
| ``swap_bytes=[0|1]``               | A value of 0 causes DDS to serialize data in the source machine's native endianness; a value of 1 causes DDS to serialize data in the opposite endianness. | ``0``     |
|                                    | The receiving side will adjust the data for its endianness so there is no need to match this option between machines.                                      |           |
|                                    | The purpose of this option is to allow the developer to decide which side will make the endian adjustment, if necessary.                                   |           |
+------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------+
| ``passive_connect_duration=msec``  | Timeout (milliseconds) for initial passive connection establishment.                                                                                       | ``10000`` |
|                                    | By default, this option waits for ten seconds.                                                                                                             |           |
|                                    | A value of zero would wait indefinitely (not recommended).                                                                                                 |           |
+------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------+

The ``passive_connect_duration`` option is typically set to a non-zero, positive integer.
Without a suitable connection timeout, the subscriber endpoint can potentially enter a state of deadlock while waiting for the remote side to initiate a connection.
Because there can be multiple transport instances on both the publisher and subscriber side, this option needs to be set to a high enough value to allow the publisher to iterate through the combinations until it succeeds.

In addition to the user-defined configurations, OpenDDS can implicitly define two transport configurations.
The first is the default configuration and includes all transport implementations that are linked into the process.
If none are found, then only tcp is used.
Each of these transport instances uses the default configuration for that transport implementation.
This is the global transport configuration used when the user does not define one.

The second implicit transport configuration is defined whenever an OpenDDS configuration file is used.
It is given the same name as the file being read and includes all the transport instances defined in that file, in the alphabetical order of their names.
The user can most easily utilize this configuration by specifying the ``DCPSGlobalTransportConfiguration=$file`` option in the same file.
The $file value always binds to the implicit file configuration of the current file.

Transport Instance Options
==========================

Transport Instances are specified in the OpenDDS configuration file via sections with the format of ``[transport/<name>]``, where ``<name>`` is a unique name for that instance within that process.
Each Transport Instance must specify the ``transport_type`` option with a valid transport implementation type.
The following sections list the other options that can be specified, starting with those options common to all transport types and following with those specific to each transport type.

When using dynamic libraries, the OpenDDS transport libraries are dynamically loaded whenever an instance of that type is defined in a configuration file.
When using custom transport implementations or static linking, the application developer is responsible for ensuring that the transport implementation code is linked with their executables.

Configuration Options Common to All Transports
----------------------------------------------

The following table summarizes the transport configuration options that are common to all transports:

**Table 7-13 Common Transport Configuration Options**

+----------------------------------+-------------------------------------------------------------------------------------------------------------------------------------+------------------+
| Option                           | Description                                                                                                                         | Default          |
+==================================+=====================================================================================================================================+==================+
| ``transport_type=transport``     | Type of the transport; the list of available transports can be extended programmatically via the transport framework.               | none             |
|                                  | tcp, udp, multicast, shmem, and rtps_udp are included with OpenDDS.                                                                 |                  |
+----------------------------------+-------------------------------------------------------------------------------------------------------------------------------------+------------------+
| ``queue_messages_per_pool=n``    | When backpressure is detected, messages to be sent are queued.                                                                      | ``10``           |
|                                  | When the message queue must grow, it grows by this number.                                                                          |                  |
+----------------------------------+-------------------------------------------------------------------------------------------------------------------------------------+------------------+
| ``queue_initial_pools=n``        | The initial number of pools for the backpressure queue.                                                                             | ``5``            |
|                                  | The default settings of the two backpressure queue values preallocate space for 50 messages (5 pools of 10 messages).               |                  |
+----------------------------------+-------------------------------------------------------------------------------------------------------------------------------------+------------------+
| ``max_packet_size=n``            | The maximum size of a transport packet, including its transport header, sample header, and sample data.                             | ``2147481599``   |
+----------------------------------+-------------------------------------------------------------------------------------------------------------------------------------+------------------+
| ``max_samples_per_packet=n``     | Maximum number of samples in a transport packet.                                                                                    | ``10``           |
+----------------------------------+-------------------------------------------------------------------------------------------------------------------------------------+------------------+
| ``optimum_packet_size=n``        | Transport packets greater than this size will be sent over the wire even if there are still queued samples to be sent.              | ``4096 (4 KiB)`` |
|                                  | This value may impact performance depending on your network configuration and application nature.                                   |                  |
+----------------------------------+-------------------------------------------------------------------------------------------------------------------------------------+------------------+
| ``thread_per_connection= [0|1]`` | Enable or disable the thread per connection send strategy.                                                                          | ``0``            |
|                                  | By default, this option is disabled.                                                                                                |                  |
+----------------------------------+-------------------------------------------------------------------------------------------------------------------------------------+------------------+
| ``datalink_release_delay=msec``  | The datalink_release_delay is the delay (in milliseconds) for datalink release after no associations.                               | ``10000``        |
|                                  | Increasing this value may reduce the overhead of re-establishment when reader/writer associations are added and removed frequently. |                  |
+----------------------------------+-------------------------------------------------------------------------------------------------------------------------------------+------------------+

Enabling the ``thread_per_connection`` option will increase performance when writing to multiple data readers on different process as long as the overhead of thread context switching does not outweigh the benefits of parallel writes.
This balance of network performance to context switching overhead is best determined by experimenting.
If a machine has multiple network cards, it may improve performance by creating a transport for each network card.

TCP/IP Transport Configuration Options
--------------------------------------

There are a number of configurable options for the tcp transport.
A properly configured transport provides added resilience to underlying stack disturbances.
Almost all of the options available to customize the connection and reconnection strategies have reasonable defaults, but ultimately these values should to be chosen based upon a careful study of the quality of the network and the desired QoS in the specific DDS application and target environment.

The local_address option is used by the peer to establish a connection.
By default, the TCP transport selects an ephemeral port number on the NIC with the FQDN (fully qualified domain name) resolved.
Therefore, you may wish to explicitly set the address if you have multiple NICs or if you wish to specify the port number.
When you configure inter-host communication, the local_address can not be localhost and should be configured with an externally visible address (i.e.
192.168.0.2), or you can leave it unspecified in which case the FQDN and an ephemeral port will be used.

FQDN resolution is dependent upon system configuration.
In the absence of a FQDN (e.g.
``example.objectcomputing.com``), OpenDDS will use any discovered short names (e.g.
example).
If that fails, it will use the name resolved from the loopback address (e.g.
localhost).

.. note:: OpenDDS IPv6 support requires that the underlying ACE/TAO components be built with IPv6 support enabled.
  The local_address needs to be an IPv6 decimal address or a FQDN with port number.
  The FQDN must be resolvable to an IPv6 address.

The ``tcp`` transport exists as an independent library and needs to be linked in order to use it.
When using a dynamically-linked build, OpenDDS automatically loads the transport library whenever it is referenced in a configuration file or as the default transport when no other transports are specified.

When the ``tcp`` library is built statically, your application must link directly against the library.
To do this, your application must first include the proper header for service initialization: ``<dds/DCPS/transport/tcp/Tcp.h>``.

You can also configure the publisher and subscriber transport implementations programatically, as described in :ref:`Transport Registry Example`.
Configuring subscribers and publishers should be identical, but different addresses/ports should be assigned to each Transport Instance.

The following table summarizes the transport configuration options that are unique to the ``tcp`` transport:

**Table 7-14 TCP/IP Configuration Options**

+-------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------+
| Option                              | Description                                                                                                                                                                                                                                                                                                                                      | Default    |
+=====================================+==================================================================================================================================================================================================================================================================================================================================================+============+
| ``active_conn_timeout_period=msec`` | The time period (milliseconds) for the active connection side to wait for the connection to be established.                                                                                                                                                                                                                                      | ``5000``   |
|                                     | If not connected within this period then the on_publication_lost() callbacks will be called.                                                                                                                                                                                                                                                     |            |
+-------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------+
| ``conn_retry_attempts=n``           | Number of reconnect attempts before giving up and calling the on_publication_lost() and on_subscription_lost() callbacks.                                                                                                                                                                                                                        | ``3``      |
+-------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------+
| ``conn_retry_initial_delay=msec``   | Initial delay (milliseconds) for reconnect attempt.                                                                                                                                                                                                                                                                                              | ``500``    |
|                                     | As soon as a lost connection is detected, a reconnect is attempted.                                                                                                                                                                                                                                                                              |            |
|                                     | If this reconnect fails, a second attempt is made after this specified delay.                                                                                                                                                                                                                                                                    |            |
+-------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------+
| ``conn_retry_backoff_multiplier=n`` | The backoff multiplier for reconnection tries.                                                                                                                                                                                                                                                                                                   | ``2.0``    |
|                                     | After the initial delay described above, subsequent delays are determined by the product of this multiplier and the previous delay.                                                                                                                                                                                                              |            |
|                                     | For example, with a conn_retry_initial_delay of 500 and a conn_retry_backoff_multiplier of 1.5, the second reconnect attempt will be 0.5 seconds after the first retry connect fails; the third attempt will be 0.75 seconds after the second retry connect fails; the fourth attempt will be 1.125 seconds after the third retry connect fails. |            |
+-------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------+
| ``enable_nagle_algorithm=[0|1]``    | Enable or disable the Nagle’s algorithm.                                                                                                                                                                                                                                                                                                         | ``0``      |
|                                     | By default, it is disabled.                                                                                                                                                                                                                                                                                                                      |            |
|                                     |                                                                                                                                                                                                                                                                                                                                                  |            |
|                                     | Enabling the Nagle’s algorithm may increase throughput at the expense of increased latency.                                                                                                                                                                                                                                                      |            |
+-------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------+
| ``local_address=host:port``         | Hostname and port of the connection acceptor.                                                                                                                                                                                                                                                                                                    | ``fqdn:0`` |
|                                     | The default value is the FQDN and port 0, which means the OS will choose the port.                                                                                                                                                                                                                                                               |            |
|                                     | If only the host is specified and the port number is omitted, the ‘:’ is still required on the host specifier.                                                                                                                                                                                                                                   |            |
+-------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------+
| ``max_output_pause_period=msec``    | Maximum period (milliseconds) of not being able to send queued messages.                                                                                                                                                                                                                                                                         | ``0``      |
|                                     | If there are samples queued and no output for longer than this period then the connection will be closed and ``on_*_lost()`` callbacks will be called.                                                                                                                                                                                           |            |
|                                     | The default value of zero means that this check is not made.                                                                                                                                                                                                                                                                                     |            |
+-------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------+
| ``passive_reconnect_duration=msec`` | The time period (milliseconds) for the passive connection side to wait for the connection to be reconnected.                                                                                                                                                                                                                                     | ``2000``   |
|                                     | If not reconnected within this period then the ``on_*_lost()`` callbacks will be called.                                                                                                                                                                                                                                                         |            |
+-------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------+
| ``pub_address=host:port``           | Override the address sent to peers with the configured string.                                                                                                                                                                                                                                                                                   |            |
|                                     | This can be used for firewall traversal and other advanced network configurations.                                                                                                                                                                                                                                                               |            |
+-------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------+

TCP/IP Reconnection Options
^^^^^^^^^^^^^^^^^^^^^^^^^^^

When a TCP/IP connection gets closed OpenDDS attempts to reconnect.
The reconnection process is (a successful reconnect ends this sequence):

* Upon detecting a lost connection immediately attempt reconnect.

* If that fails, then wait ``conn_retry_initial_delay`` milliseconds and attempt reconnect.

* While we have not tried more than ``conn_retry_attempts``, wait (previous wait time * ``conn_retry_backoff_multiplier``) milliseconds and attempt to reconnect.


UDP/IP Transport Configuration Options
--------------------------------------

The ``udp`` transport is a bare bones transport that supports best-effort delivery only.
Like ``tcp``, ``local_address``, it supports both IPv4 and IPv6 addresses.

``udp`` exists as an independent library and therefore needs to be linked and configured like other transport libraries.
When using a dynamic library build, OpenDDS automatically loads the library when it is referenced in a configuration file.
When the ``udp`` library is built statically, your application must link directly against the library.
Additionally, your application must also include the proper header for service initialization: ``<dds/DCPS/transport/udp/Udp.h>``.

The following table summarizes the transport configuration options that are unique to the ``udp`` transport:

**Table 7-15 UDP/IP Configuration Options**

+-----------------------------+---------------------------------------------------------------------+-----------------------------------------------------+
| Option                      | Description                                                         | Default                                             |
+=============================+=====================================================================+=====================================================+
| ``local_address=host:port`` | Hostname and port of the listening socket.                          | ``fqdn:0``                                          |
|                             | Defaults to a value picked by the underlying OS.                    |                                                     |
|                             | The port can be omitted, in which case the value should end in “:”. |                                                     |
+-----------------------------+---------------------------------------------------------------------+-----------------------------------------------------+
| ``send_buffer_size=n``      | Total send buffer size in bytes for UDP payload.                    | ``Platform value of ACE_DEFAULT_MAX_SOCKET_BUFSIZ`` |
+-----------------------------+---------------------------------------------------------------------+-----------------------------------------------------+
| ``rcv_buffer_size=n``       | Total receive buffer size in bytes for UDP payload.                 | ``Platform value of ACE_DEFAULT_MAX_SOCKET_BUFSIZ`` |
+-----------------------------+---------------------------------------------------------------------+-----------------------------------------------------+

IP Multicast Transport Configuration Options
--------------------------------------------

The ``multicast`` transport provides unified support for best-effort and reliable delivery based on a transport configuration parameter.

Best-effort delivery imposes the least amount of overhead as data is exchanged between peers, however it does not provide any guarantee of delivery.
Data may be lost due to unresponsive or unreachable peers or received in duplicate.

Reliable delivery provides for guaranteed delivery of data to associated peers with no duplication at the cost of additional processing and bandwidth.
Reliable delivery is achieved through two primary mechanisms: 2-way peer handshaking and negative acknowledgment of missing data.
Each of these mechanisms are bounded to ensure deterministic behavior and is configurable to ensure the broadest applicability possible for user environments.

``multicast`` supports a number of configuration options:

The ``default_to_ipv6`` and ``port_offset`` options affect how default multicast group addresses are selected.
If ``default_to_ipv6`` is set to “``1``” (enabled), then the default IPv6 address will be used (``[FF01::80]``).
The ``port_offset`` option determines the default port used when the group address is not set and defaults to ``49152``.

The ``group_address`` option may be used to manually define a multicast group to join to exchange data.
Both IPv4 and IPv6 addresses are supported.
As with ``tcp``, OpenDDS IPv6 support requires that the underlying ACE/TAO components be built with IPv6 support enabled.

On hosts with multiple network interfaces, it may be necessary to specify that the multicast group should be joined on a specific interface.
The option ``local_address`` can be set to the IP address of the local interface that will receive multicast traffic.

If reliable delivery is desired, the ``reliable`` option may be specified (the default).
The remainder of configuration options affect the reliability mechanisms used by the ``multicast`` transport:

The ``syn_backoff``, ``syn_interval``, and ``syn_timeout`` configuration options affect the handshaking mechanism.
``syn_backoff`` is the exponential base used when calculating the backoff delay between retries.
The ``syn_interval`` option defines the minimum number of milliseconds to wait before retrying a handshake.
The ``syn_timeout`` defines the maximum number of milliseconds to wait before giving up on the handshake.

Given the values of ``syn_backoff`` and ``syn_interval``, it is possible to calculate the delays between handshake attempts (bounded by ``syn_timeout``):

::

        delay = syn_interval * syn_backoff ^ number_of_retries

For example, if the default configuration options are assumed, the delays between handshake attempts would be: 0, 250, 1000, 2000, 4000, and 8000 milliseconds respectively.

The ``nak_depth``, ``nak_interval``, and ``nak_timeout`` configuration options affect the Negative Acknowledgment mechanism.
``nak_depth`` determines the maximum number of datagrams retained by the transport to service incoming repair requests.
The ``nak_interval`` configuration option defines the minimum number of milliseconds to wait between repair requests.
This interval is randomized to prevent potential collisions between similarly associated peers.
The *maximum* delay between repair requests is bounded to double the minimum value.

The ``nak_timeout`` configuration option defines the maximum amount of time to wait on a repair request before giving up.

The ``nak_delay_intervals`` configuration option defines the number of intervals between naks after the initial nak.

The ``nak_max`` configuration option limits the maximum number of times a missing sample will be nak'ed.
Use this option so that naks will be not be sent repeatedly for unrecoverable packets before ``nak_timeout``.

Currently, there are a couple of requirements above and beyond those already mandated by the ETF when using this transport:

* *At most*, one DDS domain may be used per multicast group;

* A given participant may only have a single ``multicast`` transport attached per multicast group; if you wish to send and receive samples on the same multicast group in the same process, independent participants must be used.

``multicast`` exists as an independent library and therefore needs to be linked and configured like other transport libraries.
When using a dynamic library build, OpenDDS automatically loads the library when it is referenced in a configuration file.
When the ``multicast`` library is built statically, your application must link directly against the library.
Additionally, your application must also include the proper header for service initialization: ``<dds/DCPS/transport/multicast/Multicast.h>``.

The following table summarizes the transport configuration options that are unique to the ``multicast`` transport:

**Table 7-16 IP Multicast Configuration Options**

+-----------------------------+-----------------------------------------------------------------------------------------------------------+-------------------------+
| Option                      | Description                                                                                               | Default                 |
+=============================+===========================================================================================================+=========================+
| ``default_to_ipv6=[0|1]``   | Enables IPv6 default group address selection.                                                             | ``0``                   |
|                             | By default, this option is disabled.                                                                      |                         |
+-----------------------------+-----------------------------------------------------------------------------------------------------------+-------------------------+
| ``group_address=host:port`` | The multicast group to join to send/receive data.                                                         | ``224.0.0.128:<port>,`` |
|                             |                                                                                                           |                         |
|                             |                                                                                                           | ``[FF01::80]:<port>``   |
+-----------------------------+-----------------------------------------------------------------------------------------------------------+-------------------------+
| ``local_address=address``   | If non-empty, address of a local network interface which is used to join the multicast group.             |                         |
+-----------------------------+-----------------------------------------------------------------------------------------------------------+-------------------------+
| ``nak_delay_intervals=n``   | The number of intervals between naks after the initial nak.                                               | ``4``                   |
+-----------------------------+-----------------------------------------------------------------------------------------------------------+-------------------------+
| ``nak_depth=n``             | The number of datagrams to retain in order to service repair requests (reliable only).                    | ``32``                  |
+-----------------------------+-----------------------------------------------------------------------------------------------------------+-------------------------+
| ``nak_interval=msec``       | The minimum number of milliseconds to wait between repair requests (reliable only).                       | ``500``                 |
+-----------------------------+-----------------------------------------------------------------------------------------------------------+-------------------------+
| ``nak_max=n``               | The maximum number of times a missing sample will be nak'ed.                                              | ``3``                   |
+-----------------------------+-----------------------------------------------------------------------------------------------------------+-------------------------+
| ``nak_timeout=msec``        | The maximum number of milliseconds to wait before giving up on a repair response (reliable only).         | ``30000``               |
|                             | The default is 30 seconds.                                                                                |                         |
+-----------------------------+-----------------------------------------------------------------------------------------------------------+-------------------------+
| ``port_offset=n``           | Used to set the port number when not specifying a group address.                                          | ``49152``               |
|                             | When a group address is specified, the port number within it is used.                                     |                         |
|                             | If no group address is specified, the port offset is used as a port number.                               |                         |
|                             | This value should not be set less than 49152.                                                             |                         |
+-----------------------------+-----------------------------------------------------------------------------------------------------------+-------------------------+
| ``rcv_buffer_size=n``       | The size of the socket receive buffer in bytes.                                                           | ``0``                   |
|                             | A value of zero indicates that the system default value is used.                                          |                         |
+-----------------------------+-----------------------------------------------------------------------------------------------------------+-------------------------+
| ``reliable=[0|1]``          | Enables reliable communication.                                                                           | ``1``                   |
+-----------------------------+-----------------------------------------------------------------------------------------------------------+-------------------------+
| ``syn_backoff=n``           | The exponential base used during handshake retries; smaller values yield shorter delays between attempts. | ``2.0``                 |
+-----------------------------+-----------------------------------------------------------------------------------------------------------+-------------------------+
| ``syn_interval=msec``       | The minimum number of milliseconds to wait between handshake attempts during association.                 | ``250``                 |
+-----------------------------+-----------------------------------------------------------------------------------------------------------+-------------------------+
| ``syn_timeout=msec``        | The maximum number of milliseconds to wait before giving up on a handshake response during association.   | ``30000``               |
|                             | The default is 30 seconds.                                                                                |                         |
+-----------------------------+-----------------------------------------------------------------------------------------------------------+-------------------------+
| ``ttl=n``                   | The value of the time-to-live (ttl) field of any datagrams sent.                                          | ``1``                   |
|                             | The default value of one means that all data is restricted to the local network.                          |                         |
+-----------------------------+-----------------------------------------------------------------------------------------------------------+-------------------------+
| ``async_send=[0|1]``        | Send datagrams using Async I/O (on platforms that support it efficiently).                                |                         |
+-----------------------------+-----------------------------------------------------------------------------------------------------------+-------------------------+

RTPS_UDP Transport Configuration Options
----------------------------------------

The OpenDDS implementation of the OMG DDSI-RTPS (``formal/2014-09-01``) specification includes the transport protocols necessary to fulfill the specification requirements and those needed to be interoperable with other DDS implementations.
The ``rtps_udp`` transport is one of the pluggable transports available to a developer and is necessary for interoperable communication between implementations.
This section will discuss the options available to the developer for configuring OpenDDS to use this transport.

To provide an RTPS variant of the single configuration example from Section , the configuration file below simply modifies the ``transport_type`` property to the value ``rtps_udp``.
All other items remain the same.

.. code-block:: ini

    [common]
    DCPSGlobalTransportConfig=myconfig

    [config/myconfig]
    transports=myrtps

    [transport/myrtps]
    transport_type=rtps_udp
    local_address=myhost

To extend our examples to a mixed transport configuration as shown in Section , below shows the use of an ``rtps_udp`` transport mixed with a ``tcp`` transport.
The interesting pattern that this allows for is a deployed OpenDDS application that can be, for example, communicating using ``tcp`` with other OpenDDS participants while communicating in an interoperability configuration with a non-OpenDDS participant using ``rtps_udp``.

.. code-block:: ini

    [common]
    DCPSGlobalTransportConfig=myconfig

    [config/myconfig]
    transports=mytcp,myrtps

    [transport/myrtps]
    transport_type=rtps_udp

    [transport/mytcp]
    transport_type=tcp

Some implementation notes related to using the ``rtps_udp`` transport protocol are as follows:

* ``WRITER_DATA_LIFECYCLE`` (8.7.2.2.7) notes that the same Data sub-message should dispose and unregister an instance.
  OpenDDS may use two Data sub-messages.

* RTPS transport instances can not be shared by different Domain Participants.

* Transport auto-selection (negotiation) is partially supported with RTPS such that the ``rtps_udp`` transport goes through a handshaking phase only in reliable mode.

**Table 7-17 RTPS_UDP Configuration Options**

+-------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------+
| Option                              | Description                                                                                                                                                   | Default                              |
+=====================================+===============================================================================================================================================================+======================================+
| ``use_multicast=[0|1]``             | The ``rtps_udp`` transport can use Unicast or Multicast.                                                                                                      | ``1``                                |
|                                     | When set to 0 (false) the transport uses Unicast, otherwise a value of 1 (true) will use Multicast.                                                           |                                      |
+-------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------+
| ``multicast_group_address``         | When the transport is set to multicast, this is the multicast network address that should be used.                                                            | ``239.255.0.2:7401``                 |
|                                     | If no port is specified for the network address, port 7401 will be used.                                                                                      |                                      |
| ``=network address``                |                                                                                                                                                               |                                      |
+-------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------+
| ``multicast_interface=iface``       | Specifies the network interface to be used by this transport instance.                                                                                        | The system default interface is used |
|                                     | This uses a platform-specific format that identifies the network interface.                                                                                   |                                      |
|                                     | On Linux systems this would be something like eth ``0``.                                                                                                      |                                      |
|                                     |                                                                                                                                                               |                                      |
|                                     | If this value is not configured, the Common Configuration value ``DCPSDefaultAddress`` is used to set the multicast interface.                                |                                      |
+-------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------+
| ``local_address=addr:port``         | Bind the socket to the given address and port.                                                                                                                | System default                       |
|                                     | Port can be omitted but the trailing “:” is required.                                                                                                         |                                      |
+-------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------+
| ``nak_depth=n``                     | The number of datagrams to retain in order to service repair requests (reliable only).                                                                        | ``32``                               |
+-------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------+
| ``nak_response_delay=msec``         | Protocol tuning parameter that allows the RTPS Writer to delay the response (expressed in milliseconds) to a request for data from a negative acknowledgment. | ``200``                              |
|                                     |                                                                                                                                                               |                                      |
|                                     | (see table 8.47 in the OMG DDSI-RTPS specification)                                                                                                           |                                      |
+-------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------+
| ``heartbeat_period=msec``           | Protocol tuning parameter that specifies in milliseconds how often an RTPS Writer announces the availability of data.                                         | ``1000``                             |
|                                     |                                                                                                                                                               |                                      |
|                                     | (see table 8.47 in the OMG DDSI-RTPS specification)                                                                                                           |                                      |
+-------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------+
| ``heartbeat_response_delay=``       | Protocol tuning parameter in milliseconds that allows the RTPS Reader to delay the sending of a positive or negative acknowledgment.                          | ``500``                              |
|                                     | This parameter is used to reduce the occurrences of network storms.                                                                                           |                                      |
| ``msec``                            |                                                                                                                                                               |                                      |
|                                     | (see Section 8.4.12.2 of the OMG DDSI-RTPS specification (``formal/2014-09-01``))                                                                             |                                      |
+-------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------+
| ``handshake_timeout=msec``          | The maximum number of milliseconds to wait before giving up on a handshake response during association.                                                       | ``30000``                            |
|                                     | The default is 30 seconds.                                                                                                                                    |                                      |
+-------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------+
| ``max_message_size``                | The maximum message size.                                                                                                                                     | ``65466``                            |
|                                     | The default is the maximum UDP message size.                                                                                                                  |                                      |
+-------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------+
| ``quick_reply_ratio``               | Tuning parameter that governs how fast new announcements  occur relative to the heartbeat_ period and heartbeat_response_delay.                               | ``0.1``                              |
+-------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------+
| ``ttl=n``                           | The value of the time-to-live (ttl) field of any multicast datagrams sent.                                                                                    | ``1``                                |
|                                     | This value specifies the number of hops the datagram will traverse before being discarded by the network.                                                     |                                      |
|                                     | The default value of 1 means that all data is restricted to the local network subnet.                                                                         |                                      |
+-------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------+
| ``DataRtpsRelayAddress=host:port``  | Specifies the address of the RtpsRelay for RTPS messages.                                                                                                     |                                      |
|                                     | See section :ref:`The RtpsRelay`.                                                                                                                             |                                      |
+-------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------+
| ``RtpsRelayOnly=[0|1]``             | Only send RTPS message to the RtpsRelay (for debugging).                                                                                                      | 0                                    |
|                                     | See section :ref:`The RtpsRelay`.                                                                                                                             |                                      |
+-------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------+
| ``UseRtpsRelay=[0|1]``              | Send messages to the RtpsRelay.                                                                                                                               | 0                                    |
|                                     | Messages will only be sent if DataRtpsRelayAddress is set.                                                                                                    |                                      |
|                                     | See section :ref:`The RtpsRelay`.                                                                                                                             |                                      |
+-------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------+
| ``DataStunServerAddress=host:port`` | Specifies the address of the STUN server to use for RTPS when using ICE.                                                                                      |                                      |
|                                     | See section :ref:`Interactive Connectivity Establishment (ICE) for RTPS`.                                                                                     |                                      |
+-------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------+
| ``UseIce=[0|1]``                    | Enable or disable ICE for this transport instance.                                                                                                            | ``0``                                |
|                                     | See section :ref:`Interactive Connectivity Establishment (ICE) for RTPS`.                                                                                     |                                      |
+-------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------+

Shared-Memory Transport Configuration Options
---------------------------------------------

The following table summarizes the transport configuration options that are unique to the ``shmem`` transport.
This transport type is supported Unix-like platforms with POSIX/XSI shared memory and on Windows platforms.
The shared memory transport type can only provide communication between transport instances on the same host.
As part of transport negotiation (see :ref:`Using Mixed Transports`), if there are multiple transport instances available for communication between hosts, the shared memory transport instances will be skipped so that other types can be used.

**Table 7-18 Shared-Memory Transport Configuration Options**

+---------------------------------+---------------------------------------------------------------------------+-----------------------+
| Option                          | Description                                                               | Default               |
+=================================+===========================================================================+=======================+
| ``pool_size=bytes``             | The size of the single shared-memory pool allocated.                      | ``16777216 (16 MiB)`` |
+---------------------------------+---------------------------------------------------------------------------+-----------------------+
| ``datalink_control_size=bytes`` | The size of the control area allocated for each data link.                | ``4096 (4 KiB)``      |
|                                 | This allocation comes out of the shared-memory pool defined by pool_size. |                       |
+---------------------------------+---------------------------------------------------------------------------+-----------------------+

***********************************************
Discovery and Transport Configuration Templates
***********************************************

OpenDDS supports dynamic configuration of RTPS discovery and transports by means of configuration templates in OpenDDS configuration files.
This feature adds 3 optional file sections, ``[DomainRange]``, ``[transport_template]``, and ``[Customization]``, as well as a new transport property, ``instantiation_rule``, which specifies when transport instances are created.
Configuration templates are processed at application startup; however, creation of domain, discovery, and transport objects is deferred until a participant is created in a corresponding domain.

A traditional OpenDDS application with 5 participants in different domains will have a config.ini file with 5 separate but nearly identical ``[domain]`` sections.
The same functionality can be accomplished with a single ``[DomainRange/1-5]`` section using templates.

``[Customization]`` sections can be used in ``[rtps_discovery]`` template sections to add the domain ID to the multicast override address.
This creates a unique address for each domain.
``[Customization]`` sections can also be used with ``[transport_template]`` sections to modify the transport multicast group addresses and address ports by domain ID.
The ``[transport_template]`` rule, ``instantiation_rule=per_participant``, configures OpenDDS to create a separate transport instance for each domain participant.
This allows applications to have multiple participants per domain when using RTPS.

Configuring Discovery for a Set of Similar Domains
==================================================

Domain range sections are similar to domain sections and use the same configuration properties with 3 notable differences.

* Domain ranges must have a beginning and end domain, such as ``[DomainRange/1-5]``.

* Domain ranges use the ``DiscoveryTemplate`` property rather than the ``DiscoveryConfig`` property to denote the corresponding ``[rtps_discovery]`` section.

* Domain ranges can have an optional ``Customization`` property that maps to a named ``[Customization]`` section

See section :ref:`Example Config.ini` for a ``[DomainRange]`` example.

Configuring a Set of Similar Transports
=======================================

Transport template sections are specified as ``[transport_template/name]``.
They are similar to ``[transport]`` sections and use the same configuration properties as well as an optional ``Customization`` property that maps to a named ``[Customization]`` section.
To associate a transport template with a domain range in a configuration file, set the ``DCPSGlobalTransportConfig`` property in the ``[common]`` section to the name of the ``[config]`` whose transports property is the name of the transport template.
For example, for a global config setting

.. code-block:: ini

    [common]

``DCPSGlobalTransportConfig=primary_config``

a corresponding config could be

.. code-block:: ini

    [config/primary_config]
    transports=auto_config_rtps

and the partial transport template would be

.. code-block:: ini

    [transport_template/auto_config_rtps]
    transport_type=rtps_udp

Domain participants that belong to a domain that is configured by a template can bind to non-global transport configurations using the ``bind_config`` function.
See section :ref:`Using Multiple Configurations` for a discussion of ``bind_config``.

If the ``[transport_template]`` sets the property ``instantiation_rule=per_participant``, a separate transport instance will be created for each participant in the domain.

See section :ref:`Example Config.ini` for a ``[transport_template]`` example.

Adding Customizations
=====================

``[Customization]`` sections can modify the InteropMulticastOverride property in [rtps_discovery] sections and the multicast_group_address property in ``[transport_template]`` sections.

* ``InteropMulticastOverride=AddDomainId`` adds the domain id to the last octet of the ``InteropMulticastOverride`` address

* ``multicast_group_address=add_domain_id_to_ip_addr`` adds the domain ID to the last octet of the multicast group address

* ``multicast_group_address=add_domain_id_to_port`` uses the domain ID in the port calculation for the multicast group address


Example Config.ini
==================

The following is an example configuration file for domains 2 through 10.
It includes customizations to add the domain ID to the discovery ``InteropMulticastOverride`` address and customizations to add the domain ID to the transport’s multicast group IP address and port.

.. code-block:: ini

    [common]
    DCPSGlobalTransportConfig=the_config

    [DomainRange/2-10]
    DiscoveryTemplate=DiscoveryConfigTemplate

    [Customization/discovery_customization]
    InteropMulticastOverride=AddDomainId

    [Customization/transport_customization]
    multicast_group_address=add_domain_id_to_ip_addr,add_domain_id_to_port

    [rtps_discovery/DiscoveryConfigTemplate]
    InteropMulticastOverride=239.255.4.0
    Customization=discovery_customization
    SedpMulticast=1

    [config/the_config]
    transports=auto_config_rtps

    [transport_template/auto_config_rtps]
    transport_type=rtps_udp
    instantiation_rule=per_participant
    Customization=transport_customization
    multicast_group_address=239.255.2.0

*******
Logging
*******

By default, the OpenDDS framework will only log when there is a serious error that is not indicated by a return code.
An OpenDDS user may increase the amount of logging via controls at the DCPS, Transport, or Security layers.

DCPS Layer Logging
==================

Logging in the DCPS layer of OpenDDS is controlled by the ``DCPSDebugLevel`` configuration option and command-line option.
It can also be set programmatically in application code using:

.. code-block:: cpp

    OpenDDS::DCPS::set_DCPS_debug_level(level)

The *level* defaults to a value of 0 and has values of 0 to 10 as defined below:

* 0 - logs that indicate serious errors that are not indicated by return codes (almost none).

* 1 - logs that should happen once per process or are warnings

* 2 - logs that should happen once per DDS entity

* 4 - logs that are related to administrative interfaces

* 6 - logs that should happen every Nth sample write/read

* 8 - logs that should happen once per sample write/read

* 10 - logs that may happen more than once per sample write/read


Transport Layer Logging
=======================

OpenDDS transport layer logging is controlled via the ``DCPSTransportDebugLevel`` configuration option.
For example, to add transport layer logging to any OpenDDS application, add the following option to the command line:

::

    -DCPSTransportDebugLevel level

The transport layer logging level can also be programmatically configured by appropriately setting the variable:

.. code-block:: cpp

    OpenDDS::DCPS::Transport_debug_level = level;

Valid transport logging levels range from 0 to 5 with increasing verbosity of output.

.. note:: Transport logging level 6 is available to generate system trace logs.
  Using this level is not recommended as the amount of data generated can be overwhelming and is mostly of interest only to OpenDDS developers.
  Setting the logging level to 6 requires defining the ``DDS_BLD_DEBUG_LEVEL`` macro to ``6`` and rebuilding OpenDDS.

Security Logging
================

When OpenDDS is compiled with security enabled, logging for security can be enabled using ``DCPSecurityDebug``(See Table 7-2 Common Configuration Options).
Unlike the other logging controls, security logging is divided into categories, although ``DCPSSecurityDebugLevel`` is also provided, which controls the categories in a similar manner and using the same scale as ``DCPSDebugLevel``.

**Table 7-19 Security Debug Logging Categories**

+------------------+-------------+---------------------------------------------------------------------------------------------------------------------------------+
| Option           | Debug Level | Description                                                                                                                     |
+==================+=============+=================================================================================================================================+
| N/A              | 0           | The default.                                                                                                                    |
|                  |             | Security related messages are not logged.                                                                                       |
+------------------+-------------+---------------------------------------------------------------------------------------------------------------------------------+
| ``access_warn``  | 1           | Logs warnings from permission and governance file parsing.                                                                      |
+------------------+-------------+---------------------------------------------------------------------------------------------------------------------------------+
| ``auth_warn``    | 3           | Log warnings from the authentication and handshake that happen when two secure participants discover each other.                |
+------------------+-------------+---------------------------------------------------------------------------------------------------------------------------------+
| ``encdec_error`` | 3           | Logs errors from the encryption and decryption of RTPS messages.                                                                |
+------------------+-------------+---------------------------------------------------------------------------------------------------------------------------------+
| ``bookkeeping``  | 4           | Logs generation of crypto handles and keys for local DDS entities and tracking crypto handles and keys for remote DDS entities. |
+------------------+-------------+---------------------------------------------------------------------------------------------------------------------------------+
| ``auth_debug``   | 4           | Logs debug information from the authentication and handshake that happen when two secure participants discover each other.      |
+------------------+-------------+---------------------------------------------------------------------------------------------------------------------------------+
| ``encdec_warn``  | 4           | Logs warnings from the encryption and decryption of RTPS messages.                                                              |
+------------------+-------------+---------------------------------------------------------------------------------------------------------------------------------+
| ``encdec_debug`` | 8           | Logs debug information from the encryption and decryption of RTPS messages.                                                     |
+------------------+-------------+---------------------------------------------------------------------------------------------------------------------------------+
| ``showkeys``     | 9           | Logs the whole key when generating it, receiving it, and using it.                                                              |
+------------------+-------------+---------------------------------------------------------------------------------------------------------------------------------+
| ``chlookup``     | 10          | Very verbosely prints the steps being taken when looking up a crypto handle for decrypting.                                     |
|                  |             | This is most useful to see what keys a participant has.                                                                         |
+------------------+-------------+---------------------------------------------------------------------------------------------------------------------------------+
| ``all``          | 10          | Enable all the security related logging.                                                                                        |
+------------------+-------------+---------------------------------------------------------------------------------------------------------------------------------+

Categories are passed to ``DCPSecurityDebug`` using a comma limited list:

::

    -DCPSSecurityDebug=access_warn,showkeys

Unknown categories will cause error messages, but will not cause the ``ParticipantFactory`` to fail to initialize.

Like the other debug levels, security logging can also be programmatically configured.
All the following are equivalent:

.. code-block:: cpp

    OpenDDS::DCPS::security_debug.access_warn = true;
    OpenDDS::DCPS::security_debug.set_debug_level(1);
    OpenDDS::DCPS::security_debug.parse_flags(ACE_TEXT(“access_warn”));

