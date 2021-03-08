######
XTypes
######

********
Overview
********

The DDS specification defines a way to build distributed applications using a data-centric publish and subscribe model.
In this model, publishing and subscribing applications communicate via Topics and each Topic has a data type.
An assumption built into this model is that all applications agree on data type definitions for each Topic that they use.
This assumption is not practical as systems must be able to evolve while remaining compatible and interoperable.

The DDS XTypes (Extensible and Dynamic Topic Types) specification loosens the requirement on applications to have a common notion of data types.
Using XTypes, the application developer adds IDL annotations that indicate where the types may vary between publisher and subscriber and how those variations are handled by the middleware.

This release of OpenDDS implements the XTypes specification version 1.3 at the Basic Conformance level, except for the Dynamic Types API.
Some features described by the specification are not yet implemented in OpenDDS -- those are noted below in section :ref:`Unsupported Features`.
This includes IDL annotations that are not yet implemented.
The “Specification Differences” section (:ref:`Differences from the specification`) describes situations where the implementation of XTypes in OpenDDS departs from or infers something about the specification.
Specification issues have been raised for these situations.

********
Features
********

Extensibility
=============

There are 3 kinds of extensibility for types: Appendable, Mutable, and Final

* *Appendable* denotes a constructed type which may have additional members added onto or removed from the end.

* *Mutable* denotes a constructed type that allows for members to be added, removed, and reordered so long as the keys and the required members of the sender and receiver remain.
  Mutable extensibility is accomplished by assigning a stable identifier to each member.

* *Final* denotes a constructed type that can not add, remove, or reorder members,.
  This can be considered a non-extensible constructed type, with behavior similar to that of a type created before XTypes.

Extensibility is set by the user in the IDL with the annotations: @appendable, @mutable, @final

The default extensibility is Appendable.
This default extensibility can be changed with the IDL compiler command line option --default-extensibility EXTENSIBILITY Where EXTENSIBILITY is "final", "appendable" or "mutable".

Structs and unions are the only types which can use any of the extensibilies.

Assignability
=============

Assignability describes the ability of values of one type to be coerced to values of a possibility different type.

Assignability between the type of a writer and reader is checked as part of discovery.
If the types are assignable but not identical, then the “Try Construct” mechanism will be used to coerce values of the writer’s type to values of the reader’s type.

In order for two constructed types to be assignable they must

* Have the same extensibility.

* Have the same set of keys.

Each member of a constructed type has an identifier.
This identifier may be assigned automatically or explicitly.

Union assignability depends on two dimensions.
First, unions are only assignable if their discriminators are assignable.
Second, for any branch label or default that exists in both unions, the members selected by that branch label must be assignable.

Interoperability with non-XTypes Implementations
================================================

Communication with a non-XTypes DDS (either an older OpenDDS or another DDS implementation which has RTPS but not XTypes 1.2+) requires compatible IDL types and the use of RTPS Discovery.
Compatible IDL types means that the types are structurally equivalent and serialize to the same bytes using XCDR version 1.

Additionally, the XTypes-enabled participant needs to be set up as follows:

* Types cannot use Mutable extensibility

* Data Writers must have their Data Representation QoS policy set to DDS::XCDR_DATA_REPRESENTATION

* Data Readers must include DDS::XCDR_DATA_REPRESENTATION in the list of data representations in their Data Representation QoS (This is true by default)

The “Data Representation" section below shows how to change the data representation.

************************
Examples and Explanation
************************

Suppose you are in charge of deploying a set of weather stations that publish temperature, pressure, and humidity.
The following examples show how various features of XTypes may be applied to address changes in the schema published by the weather station.
Specifically, without XTypes, one would either need to create a new type with its own DataWriters/DataReaders or update all applications simultaneously.
With proper planning and XTypes, one can simply modify the existing type (within limits) and writers and readers using earlier versions of the topic type will remain compatible with each other and be compatible with writers and readers using new versions of the topic type.

Mutable Extensibility
=====================

The type published by the weather stations can be made extensible with the @mutable annotation:

.. code-block:: omg-idl

    // Version 1
    @topic
    @mutable
    struct StationData {
      short temperature;
      double pressure;
      double humidity;
    };

Suppose that some time in the future, a subset of the weather stations are upgraded to monitor wind speed and direction:

.. code-block:: omg-idl

    enum WindDir {N, NE, NW, S, SE, SW, W, E};
    // Version 2@topic
    @mutable
    struct StationData {  short temperature;
      double pressure;
      double humidity;
      short wind_speed;
      WindDir wind_direction;};

When a Version 2 writer interacts with a Version 1 reader, the additional fields will be ignored by the reader.
When a Version 1 writer interacts with a Version 2 reader, the additional fields will be initialized to a "logical zero" value for its type (empty string, FALSE boolean) - see Table 9 of the XTypes specification for details.

Assignability
=============

The first and second versions of the StationData type are *assignable*meaning that it is possible to construct a version 2 value from a version 1 value and vice-versa.
The assignability of non-constructed types (e.g., integers, enums, strings) is based on the types being identical or identical up to parameterization, i.e., bounds of strings and sequences may differ.
The assignability of constructed types like structs and unions is based on finding corresponding members with assignable types.
Corresponding members are those that have the same id.

A type marked as @mutable allows for members to be added, removed, or reordered so long as member ids are preserved through all of the mutations.

Member IDs
==========

Member ids are assigned using various annotations.
A policy for a type can be set with either @autoid(SEQUENTIAL) or @autoid(HASH):

.. code-block:: omg-idl

    // Version 3
    @topic
    @mutable
    @autoid(SEQUENTIAL)
    struct StationData {  short temperature;
      double pressure;
      double humidity;};

    // Version 4
    @topic
    @mutable
    @autoid(HASH)
    struct StationData {  short temperature;
      double pressure;
      double humidity;};

SEQUENTIAL causes ids to be assigned based on the position in the type.
HASH causes ids to be computed by hashing the name of the member.
If no @autoid annotation is specified, the policy is SEQUENTIAL.

Suppose that Version 3 was used in the initial deployment of the weather stations and the decision was made to switch to @autoid(HASH) when adding the new fields for wind speed and direction.
In this case, the ids of the pre-existing members can be set with @id:

.. code-block:: omg-idl

    enum WindDir {N, NE, NW, S, SE, SW, W, E};

    // Version 5@topic
    @mutable
    @autoid(HASH)
    struct StationData {
      @id(0) short temperature;
      @id(1) double pressure;
      @id(2) double humidity;
      short wind_speed;
      WindDir wind_direction;
    };

See the “Member ID Annotations” section for more details.

Appendable Extensibility
========================

Mutable extensibility requires a certain amount of overhead both in terms of processing and network traffic.
A more efficient but less flexible form of extensibility is @appendable.
Extensibility with @appendable is limited in that members can only be added to or removed from the end of the type.
With @appendable, the initial version of the weather station IDL would be:

.. code-block:: omg-idl

    // Version 6
    @topic
    @appendable
    struct StationData {  short temperature;
      double pressure;
      double humidity;};

And the subsequent addition of the wind speed and direction members would be:

.. code-block:: omg-idl

    enum WindDir {N, NE, NW, S, SE, SW, W, E};

    // Version 7@topic
    @appendable
    struct StationData {  short temperature;
      double pressure;
      double humidity;
      short wind_speed;
      WindDir wind_direction;};

As with @mutable, when a Version 7 Writer interacts with a Version 6 Reader, the additional fields will be ignored by the reader.
When a Version 6 Writer interacts with a Version 7 Reader, the additional fields will be initialized to default values based on Table 9 of the XTypes specification.

Appendable is the default extensibility.

Final Extensibility
===================

The third kind of extensibility is @final.
Annotating a type with @final means that it will not be compatible with (assignable to/from) a type that's structurally different.
The @final annotation can be used to define types for pre-XTypes compatibility or in situations where the overhead of @mutable or @appendable is unacceptable.

Try Construct
=============

From a reader’s perspective, there are three possible scenarios when attempting to initialize a member.
First, the member type is identical to the member type of the reader.
This is the trivial case the value from the writer is copied to the value for the reader.
Second, the writer does not have the member.
In this case, the value for the reader is initialized to a default value based on Table 9 of the XTypes specification (this is the "logical zero" value for the type).
Third, the type offered by the writer is assignable but not identical to the type required by the reader.
In this case, the reader must try to construct its value from the corresponding value provided by the writer.

Suppose that the weather stations also publish a topic containing station information:

.. code-block:: omg-idl

    typedef string<8> StationID;
    typedef string<256> StationName;

    // Version 1
    @topic
    @mutable
    struct StationInfo {  @try_construct(TRIM) StationID station_id;
      StationName station_name;};

Eventually, the pool of station IDs is exhausted so the IDL must be refined as follows:

.. code-block:: omg-idl

    typedef string<16> StationID;
    typedef string<256> StationName;

    // Version 2
    @topic
    @mutable
    struct StationInfo {  @try_construct(TRIM) StationID station_id;
      StationName station_name;};

If a Version 2 writer interacts with a Version 1 reader, the station ID will be truncated to 8 characters.
While perhaps not ideal, it will still allow the systems to interoperate.

There are two other forms of try-construct behavior.
Fields marked as @try_construct(USE_DEFAULT) will receive a default value if value construction fails.
In the previous example, this means the reader would receive an empty string for the station ID if it exceeds 8 characters.
Fields marked as @try_construct(DISCARD) cause the entire sample to be discarded.
In the previous example, the Version 1 reader will never see a sample from a Version 2 writer where the original station ID contains more than 8 characters.
@try_construct(DISCARD) is the default behavior.

*******************
Data Representation
*******************

Data representation is the way a data sample can be encoded for transmission.
Data representation can be XML, XCDR1, or XCDR2.

* XML is unsupported and should not be used

* XCDR1 with appendable extensibility should not be used

* XCDR2 is completely supported and preferred

XCDR2 is a more robust version of XCDR1 and should be used in preference to XCDR1 unless there is a reason to do otherwise.

Data representation is a QoS policy alongside the other QoS options.
Its listed values represent allowed serialized forms of the data sample.
The DataWriter and DataReader need to have at least one matching data representation for communication between them to be possible.

The default value of the DataRepresentationQoS policy is an empty sequence.
This is interpreted by the middleware as XCDR2 for DataWriters and the alternatives XCDR1 | XCDR2 for DataReaders.
A writer or reader without an explicitly-set DataRepresentationQoS will therefore be able to communicate with another reader or writer which is compatible with XCDR2.
The example below shows a possible configuration for an XCDR1 DataWriter.

.. code-block:: cpp

    DDS::DataWriterQos qos;
    pub->get_default_datawriter_qos(qos);
    qos.representation.value.length(1);
    qos.representation.value[0] = DDS::XCDR1_DATA_REPRESENTATION;
    DDS::DataWriter_var dw = pub->create_datawriter(topic, qos, 0, 0);

In addition to a DataWriter/DataReader QoS setting for data representation, each type defined in IDL can have its own data representation specified via an annotation.
This value restricts which data representations can be used for that type.
A DataWriter/DataReader must have at least one data representation in common with the type it uses.

The default value for an unspecified data representation annotation is to allow all forms of serialization.

The type's set of allowed data representations can be specified by the user in IDL with the notation: “@OpenDDS::data_representation(XCDR2)” where XCDR2 is replaced with the specific data representation.

***************
IDL Annotations
***************

Indicating which Types can be topic types
=========================================

@topic
------

Applies To: struct or union type declarations

The topic annotation marks a topic type for samples to be transmitted from a publisher or received by a subscriber.
A topic type may contain other topic and non-topic types.
See section :ref:`Defining Data Types with IDL` for more details.

@nested
-------

Applies To: struct or union type declarations

The @nested annotation marks a type that will always be contained within another.
This can be used to prevent a type from being used as a topic.
One reason to do so is to reduce the amount of code generated for that type.

@default_nested
---------------

Applies To: modules

The @default_nested(TRUE) or @default_nested(FALSE) sets the default nesting behavior for a module.
Types within a module marked with @default_nested(FALSE) can still set their own behavior with @nested.

Specifying allowed Data Representations
=======================================

Data Representation annotations mark the formats in which data samples of this type can be represented in a serialized form.
The Data Representation annotations listed on the type will be compared to those in the QoS policies of the reader or writer that is trying to use the type.
If a data representation is shared between the type and entity, then they can be used together.
OpenDDS’s default data representation for entities is XCDR2.
If no data representation is specified for a type, there are no restrictions on which data representations that a QoS can use with the type.

@OpenDDS::data_representation(XML)
----------------------------------

Applies To: topic types

Limitations: XML is not currently supported

@OpenDDS::data_representation(XCDR1)
------------------------------------

Applies To: topic types

Limitations: XCDR1 is not recommended.
See section :ref:`Data Representation` for details

@OpenDDS::data_representation(XCDR2)
------------------------------------

Applies To: topic types

XCDR2 is currently the recommended data representation.

Determining Extensibility
=========================

The extensibility annotations determine how a type may be changed and still be compatible.
If no extensibility annotation is set, the type will default to appendable.
The default can be changed with the command line option --default-extensibility *type*, where *type* can be final, appendable, or mutable.

@mutable
--------

Alias: @extensibility(MUTABLE)

Applies To: type declarations

This annotation indicates a type may have non-key or non-must-understand members removed.
It may also have additional members added.

@appendable
-----------

Alias: @extensibility(APPENDABLE)

Applies To: type declarations

This annotation indicates a type may have additional members added or members at the end of the type removed.

Limitations: Appendable is not currently supported when XCDR1 is used as the data representation.

@final
------

Alias: @extensibility(FINAL)

Applies To: type declarations

This annotation marks a type that cannot be changed and still be compatible.
Final is most similar to pre-XTypes.

Customizing XTypes per-member
=============================

Try Construct annotations dictate how members of one object should be converted from members of a different but assignable object.
If no try construct annotation is added, it will default to discard.

@try_construct(USE_DEFAULT)
---------------------------

Applies to: structure and union members, sequence and array elements

The use_default try construct annotation will set the member whose deserialization failed to a default value which is determined by the XTypes specification.
Sequences will be of length 0, with the same type as the original sequence.
Primitives will be set equal to 0.
Strings will be replaced with the empty string.
Arrays will be of the same length but have each element set to the default value.
Enums will be set to the first enumerator defined.

@try_construct(TRIM)
--------------------

Applies to: structure and union members, sequence and array elements

The trim try construct annotation will, if possible, shorten a received value to one fitting the receiver’s bound.
As such, trim only makes logical sense on bounded strings and bounded sequences.

@try_construct(DISCARD)
-----------------------

Applies to: structure and union members, sequence and array elements

The discard try construct annotation will “throw away” the sample if an element fails to deserialize.

Member ID assignment
====================

If no explicit id annotation is used, then Member IDs will automatically be assigned sequentially.

@id(value)
----------

Applies to: structure and union members

The *value* is a 32-bit integer which assigns that member’s ID.

@autoid(value)
--------------

Applies to: module declarations, structure declarations, union declarations

The autoid annotation can take two *value*s, HASH or SEQUENTIAL.
SEQUENTIAL states that the identifier shall be computed by incrementing the preceding one.
HASH states that the identifier should be calculated with a hashing algorithm – the input to this hash is the member’s name.
HASH is the default value of autoid.

@hashid(value)
--------------

Applies to: structure and union members

The @hashid sets the identifier to the hash of the *value* parameter, if one is specified.
If the*value* parameter is omitted or is the empty string, the member’s name is used as if it was the *value*.

Determining the Key Fields of a Type
====================================

@key
----

Applies to: structure members, union discriminator

The @key annotation marks a member used to determine the Instances of a topic type.
See section :ref:`Keys` for more details on the general concept of a Key.
For XTypes specifically, two types can only be compatible if each contains the members that are keys within the other.

********************
Unsupported Features
********************

OpenDDS implements the XTypes specification version 1.3 at the Basic Conformance level, except for the Dynamic Types API and the specific features listed below.
The two optional profiles, XTypes 1.1 Interoperability (XCDR1) and XML, are not implemented.

Annotations
===========

* @bit_bound

* @optional

* @default_literal

* @must_understand

* @external

* @verbatim


Type System
===========

* IDL map type

* IDL bitmask type

* Struct and union inheritance


**********************************
Differences from the specification
**********************************

Spec issues tracked in OMG's Jira database can be viewed at https://issues.omg.org/issues/lists/dds-xtypes-rtf

* Inconsistent topic status isn’t set for reader/reader or writer/writer in non-XTypes use cases

* DDSXTY14-29: Define the encoding and extensibility used by Type Lookup Service

* DDSXTY14-33: Enums must have the same "bit bound" to be assignable

* DDSXTY14-27: Default data representation is XCDR2

* DDSSEC12-86: Type Lookup Service when using DDS Security

* DDSXTY14-35: Anonymous types in Strongly Connected Components

* DDSXTY14-40: Meaning of ignore_member_names in TypeConsistencyEnforcement

