.. _6:

###############
Built-In Topics
###############

.. _6.1:

************
Introduction
************

In OpenDDS, Built-In-Topics are created and published by default to exchange information about DDS participants operating in the deployment.
When OpenDDS is used in a centralized discovery approach using the ``DCPSInfoRepo`` service, the Built-In-Topics are published by this service.
For DDSI-RTPS discovery, the internal OpenDDS implementation instantiated in a process populates the caches of the Built-In Topic DataReaders.
See Section :ref:`7.3.3` for a description of RTPS discovery configuration.

The IDL struct ``BuiltinTopicKey_t`` is used by the Built-In Topics.
This structure contains an array of 16 octets (bytes) which corresponds to an InfoRepo identifier or a DDSI-RTPS GUID.

.. _6.2:

**********************************************
Built-In Topics for DCPSInfoRepo Configuration
**********************************************

When starting the ``DCPSInfoRepo`` a command line option of ``-NOBITS`` may be used to suppress publication of built-in topics.

Four separate topics are defined for each domain.
Each is dedicated to a particular entity (domain participant, topic, data writer, data reader) and publishes instances describing the state for each entity in the domain.

Subscriptions to built-in topics are automatically created for each domain participant.
A participant’s support for Built-In-Topics can be toggled via the ``DCPSBit`` configuration option (see the table in Section :ref:`7.2`) (Note: this option cannot be used for RTPS discovery).
To view the built-in topic data, simply obtain the built-in Subscriber and then use it to access the Data Reader for the built-in topic of interest.
The Data Reader can then be used like any other Data Reader.

Sections :ref:`6.3` through :ref:`6.6` provide details on the data published for each of the four built-in topics.
An example showing how to read from a built-in topic follows those sections.

If you are not planning on using Built-in-Topics in your application, you can configure OpenDDS to remove Built-In-Topic support at build time.
Doing so can reduce the footprint of the core DDS library by up to 30%.
See Section :ref:`1.3.2` for information on disabling Built-In-Topic support.

.. _6.3:

*********************
DCPSParticipant Topic
*********************

The ``DCPSParticipant`` topic publishes information about the Domain Participants of the Domain.
Here is the IDL that defines the structure published for this topic:

::

    
        struct ParticipantBuiltinTopicData {
          BuiltinTopicKey_t key;
          UserDataQosPolicy user_data;
        };
    

Each Domain Participant is defined by a unique key and is its own instance within this topic.

.. _6.4:

***************
DCPSTopic Topic
***************

.. note:: OpenDDS does not support this Built-In-Topic when configured for RTPS discovery.

The ``DCPSTopic`` topic publishes information about the topics in the domain.
Here is the IDL that defines the structure published for this topic:

::

    
        struct TopicBuiltinTopicData {
          BuiltinTopicKey_t key;
          string name;
          string type_name;
          DurabilityQosPolicy durability;
          QosPolicy deadline;
          LatencyBudgetQosPolicy latency_budget;
          LivelinessQosPolicy liveliness;
          ReliabilityQosPolicy reliability;
          TransportPriorityQosPolicy transport_priority;
          LifespanQosPolicy lifespan;
          DestinationOrderQosPolicy destination_order;
          HistoryQosPolicy history;
          ResourceLimitsQosPolicy resource_limits;
          OwnershipQosPolicy ownership;
          TopicDataQosPolicy topic_data;
        };
    

Each topic is identified by a unique key and is its own instance within this built-in topic.
The members above identify the name of the topic, the name of the topic type, and the set of QoS policies for that topic.

.. _6.5:

*********************
DCPSPublication Topic
*********************

The ``DCPSPublication`` topic publishes information about the Data Writers in the Domain.
Here is the IDL that defines the structure published for this topic:

::

    
        struct PublicationBuiltinTopicData {
          BuiltinTopicKey_t key;
          BuiltinTopicKey_t participant_key;
          string topic_name;
          string type_name;
          DurabilityQosPolicy durability;
          DeadlineQosPolicy deadline;
          LatencyBudgetQosPolicy latency_budget;
          LivelinessQosPolicy liveliness;
          ReliabilityQosPolicy reliability;
          LifespanQosPolicy lifespan;
          UserDataQosPolicy user_data;
          OwnershipStrengthQosPolicy ownership_strength;
          PresentationQosPolicy presentation;
          PartitionQosPolicy partition;
          TopicDataQosPolicy topic_data;
          GroupDataQosPolicy group_data;
        };
    

Each Data Writer is assigned a unique key when it is created and defines its own instance within this topic.
The fields above identify the Domain Participant (via its key) that the Data Writer belongs to, the topic name and type, and the various QoS policies applied to the Data Writer.

.. _6.6:

**********************
DCPSSubscription Topic
**********************

The ``DCPSSubscription`` topic publishes information about the Data Readers in the Domain.
Here is the IDL that defines the structure published for this topic:

::

    
        struct SubscriptionBuiltinTopicData {
          BuiltinTopicKey_t key;
          BuiltinTopicKey_t participant_key;
          string topic_name;
          string type_name;
          DurabilityQosPolicy durability;
          DeadlineQosPolicy deadline;
          LatencyBudgetQosPolicy latency_budget;
          LivelinessQosPolicy liveliness;
          ReliabilityQosPolicy reliability;
          DestinationOrderQosPolicy destination_order;
          UserDataQosPolicy user_data;
          TimeBasedFilterQosPolicy time_based_filter;
          PresentationQosPolicy presentation;
          PartitionQosPolicy partition;
          TopicDataQosPolicy topic_data;
          GroupDataQosPolicy group_data;
        };
    

Each Data Reader is assigned a unique key when it is created and defines its own instance within this topic.
The fields above identify the Domain Participant (via its key) that the Data Reader belongs to, the topic name and type, and the various QoS policies applied to the Data Reader.

.. _6.7:

***********************************
Built-In Topic Subscription Example
***********************************

The following code uses a domain participant to get the built-in subscriber.
It then uses the subscriber to get the Data Reader for the ``DCPSParticipant`` topic and subsequently reads samples for that reader.

::

    
        Subscriber_var bit_subscriber = participant->get_builtin_subscriber();
        DDS::DataReader_var dr =
          bit_subscriber->lookup_datareader(BUILT_IN_PARTICIPANT_TOPIC);
        DDS::ParticipantBuiltinTopicDataDataReader_var part_dr =
          DDS::ParticipantBuiltinTopicDataDataReader::_narrow(dr);
    
        DDS::ParticipantBuiltinTopicDataSeq part_data;
        DDS::SampleInfoSeq infos;
        DDS::ReturnCode_t ret = part_dr->read(part_data, infos, 20,
                                              DDS::ANY_SAMPLE_STATE,
                                              DDS::ANY_VIEW_STATE,
                                              DDS::ANY_INSTANCE_STATE);
    
        // Check return status and read the participant data
    

The code for the other built-in topics is similar.

.. _6.8:

********************************
OpenDDS-specific Built-In Topics
********************************

.. _6.8.1:

OpenDDSParticipantLocation Topic
================================

The Built-In Topic “OpenDDSParticipantLocation” is published by the DDSI-RTPS discovery implementation to give applications visibility into the details of how each remote participant is connected over the network.

The IDL for OpenDDSParticipantLocation is in ``dds/DdsDcpsCore.idl`` in the ``OpenDDS::DCPS`` module.
If the RtpsRelay (:ref:`15.2`) and/or IETF ICE (:ref:`15.3`) are enabled, their usage is reflected in the OpenDDSParticipantLocation topic data.

.. _6.8.2:

OpenDDSConnectionRecord Topic
=============================

The Built-In Topic “OpenDDSConnectionRecord” is published by the DDSI-RTPS discovery implementation and RTPS_UDP transport implementation when support for IETF ICE is enabled.
See section :ref:`15.3` for details on OpenDDS’s support for IETF ICE.
The IDL for OpenDDSConnectionRecord is in ``dds/DdsDcpsCore.idl`` in the ``OpenDDS::DCPS`` module.

.. _6.8.3:

OpenDDSInternalThread Topic
===========================

The Built-In Topic “OpenDDSInternalThread” is published when OpenDDS is configured with DCPSThreadStatusInterval (see section :ref:`7.2`).
When enabled, the DataReader for this Built-In Topic will report the health (responsiveness) of threads created and managed by OpenDDS within the current process.
The IDL for OpenDDSInternalThread is in ``dds/DdsDcpsCore.idl`` in the ``OpenDDS::DCPS`` module.

