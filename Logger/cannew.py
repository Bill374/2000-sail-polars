#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  5 18:52:25 2021

@author: wmorland
"""

import os
import can
from datetime import datetime
import pathlib
import typing
from typing import Optional, Callable, Union, TextIO, BinaryIO
from abc import ABC, ABCMeta, abstractmethod


StringPathLike = typing.Union[str, "os.PathLike[str]"]


class MessageWriter(can.io.generic.BaseIOHandler, can.Listener,
                    metaclass=ABCMeta):
    """The base class for all writers."""


class FileIOMessageWriter(MessageWriter, metaclass=ABCMeta):
    """The base class for all writers."""

    file: Union[TextIO, BinaryIO]


class N2KWriter(can.io.generic.BaseIOHandler, can.Listener):
    """
    Writes a comma separated text file with a line for each NMEA2000 message.

    The file format matches the Plain format which can be read by the canboat
    Analyzer.  At some point we might include another writer which outputs
    NMEA2000 Fast format where PGNs that span multiple CAN messages are
    condensed into a single line.

    The output file includes a header line.

    The columns are as follows:
    ================ ======================= =======================
    name of column   format description      example
    ================ ======================= =======================
    timestamp        yyyy-mm-dd:hh:mm:ss     2011-11-24-22:42:04.388
    priority         int                     2
    pgn              int                     127251
    source           int                     12
    destination      int                     255
    dlc              int                     8
    data             base64 encoded          7d,0b,7d,02,00,ff,ff,ff
    ================ ======================= =======================

    Each line is terminated with a platform specific line separator.
    """

    def __init__(self, file, append=False):
        """
        :param file: a path-like object or a file-like object to write to.
                     If this is a file-like object, is has to open in text
                     write mode, not binary write mode.
        :param bool append: if set to `True` messages are appended to
                            the file and no header line is written, else
                            the file is truncated and starts with a newly
                            written header line
        """
        mode = 'a' if append else 'w'
        super(N2KWriter, self).__init__(file, mode=mode)

        # Write a header row
        if not append:
            self.file.write('timestamp,priority,pgn,source,destination,dlc,'
                            'data\n')

    def on_message_received(self, msg):
        """Write message to file in NMEA2000 plain format."""
        assert msg.is_extended_id  # NEMA2000 messages are always extended ID
        assert msg.dlc == 8        # NEMA2000 messages always have 8 data bytes

        # NMEA2000 Masks for 29 bit arbitration ID
        PRIORITY = 0b11100_00000000_00000000_00000000
        PDU_F = 0b00000_11111111_00000000_00000000
        PDU_S = 0b00000_00000000_11111111_00000000
        SHORT_PGN = 0b00011_11111111_00000000_00000000
        LONG_PGN = 0b00011_11111111_11111111_00000000
        SOURCE = 0b00000_00000000_00000000_11111111

        # Pick apart the arbitration ID into the separate NMEA2000 fields
        priority = (msg.arbitration_id & PRIORITY) >> 26
        pdu_f = (msg.arbitration_id & PDU_F) >> 16
        if pdu_f <= 239:
            # The message has a specific destination
            destination = (msg.arbitration_id & PDU_S) >> 8
            pgn = (msg.arbitration_id & SHORT_PGN) >> 16
        else:
            destination = 255
            pgn = (msg.arbitration_id & LONG_PGN) >> 8
        source = msg.arbitration_id & SOURCE

        data = ','.join(format(n, '02X') for n in msg.data)

        row = ','.join([
            datetime.fromtimestamp(msg.timestamp).strftime('%Y-%m-%d %H:%M:%S.%f'),
            str(priority),
            str(pgn),
            str(source),
            str(destination),
            str(msg.dlc),
            data
        ])

        self.file.write(row)
        self.file.write('\n')


class Logger(can.io.generic.BaseIOHandler, can.Listener):
    """
    Logs CAN messages to a file.
    The format is determined from the file format which can be one of:
      * .asc: :class:`can.ASCWriter`
      * .blf :class:`can.BLFWriter`
      * .csv: :class:`can.CSVWriter`
      * .db: :class:`can.SqliteWriter`
      * .log :class:`can.CanutilsLogWriter`
      * .txt :class:`can.Printer`
      * .n2k :class:'nmea.N2KWriter'
    The **filename** may also be *None*, to fall back to :class:`can.Printer`.
    The log files may be incomplete until `stop()` is called due to buffering.
    .. note::
        This class itself is just a dispatcher, and any positional and keyword
        arguments are passed on to the returned instance.
    """

    fetched_plugins = False
    message_writers = {
        ".asc": can.ASCWriter,
        ".blf": can.BLFWriter,
        ".csv": can.CSVWriter,
        ".db": can.SqliteWriter,
        ".log": can.CanutilsLogWriter,
        ".txt": can.Printer,
        ".n2k": N2KWriter
    }

    @staticmethod
    def __new__(cls, filename: Optional[StringPathLike], *args, **kwargs):
        """
        :param filename: the filename/path of the file to write to,
                         may be a path-like object or None to
                         instantiate a :class:`~can.Printer`
        :raises ValueError: if the filename's suffix is of an unknown file type
        """
        if filename is None:
            return can.Printer(*args, **kwargs)

        if not Logger.fetched_plugins:
            Logger.message_writers.update(
                {
                    writer.name: writer.load()
                    for writer in
                    can.iter_entry_points("can.io.message_writer")
                }
            )
            Logger.fetched_plugins = True

        suffix = pathlib.PurePath(filename).suffix.lower()
        try:
            return Logger.message_writers[suffix](filename, *args, **kwargs)
        except KeyError:
            raise ValueError(
                f'No write support for this unknown log format "{suffix}"'
            ) from None


class BaseRotatingLogger(can.Listener, ABC):
    """
    Base class for rotating CAN loggers. This class is not meant to be
    instantiated directly. Subclasses must implement the `should_rollover`
    and `do_rollover` methods according to their rotation strategy.
    The rotation behavior can be further customized by the user by setting
    the `namer` and `rotator´ attributes after instantiating the subclass.
    These attributes as well as the methods `rotation_filename` and `rotate`
    and the corresponding docstrings are carried over from the python builtin
    `BaseRotatingHandler`.
    :attr Optional[Callable] namer:
        If this attribute is set to a callable, the rotation_filename() method
        delegates to this callable. The parameters passed to the callable are
        those passed to rotation_filename().
    :attr Optional[Callable] rotator:
        If this attribute is set to a callable, the rotate() method delegates
        to this callable. The parameters passed to the callable are those
        passed to rotate().
    :attr int rollover_count:
        An integer counter to track the number of rollovers.
    :attr FileIOMessageWriter writer:
        This attribute holds an instance of a writer class which manages the
        actual file IO.
    """

    supported_writers = {
        ".asc": can.ASCWriter,
        ".blf": can.BLFWriter,
        ".csv": can.CSVWriter,
        ".log": can.CanutilsLogWriter,
        ".txt": can.Printer,
        ".n2k": N2KWriter
    }
    namer: Optional[Callable] = None
    rotator: Optional[Callable] = None
    rollover_count: int = 0
    _writer: Optional[FileIOMessageWriter] = None

    def __init__(self, *args, **kwargs):
        self.writer_args = args
        self.writer_kwargs = kwargs

    @property
    def writer(self) -> FileIOMessageWriter:
        if not self._writer:
            raise ValueError("Attempt to access writer failed.")

        return self._writer

    def rotation_filename(self, default_name: StringPathLike):
        """Modify the filename of a log file when rotating.
        This is provided so that a custom filename can be provided.
        The default implementation calls the 'namer' attribute of the
        handler, if it's callable, passing the default name to
        it. If the attribute isn't callable (the default is None), the name
        is returned unchanged.
        :param default_name:
            The default name for the log file.
        """
        if not callable(self.namer):
            result = default_name
        else:
            result = self.namer(default_name)
        return result

    def rotate(self, source: StringPathLike, dest: StringPathLike):
        """When rotating, rotate the current log.
        The default implementation calls the 'rotator' attribute of the
        handler, if it's callable, passing the source and dest arguments to
        it. If the attribute isn't callable (the default is None), the source
        is simply renamed to the destination.
        :param source:
            The source filename. This is normally the base
            filename, e.g. 'test.log'
        :param dest:
            The destination filename. This is normally
            what the source is rotated to, e.g. 'test_#001.log'.
        """
        if not callable(self.rotator):
            if os.path.exists(source):
                os.rename(source, dest)
        else:
            self.rotator(source, dest)

    def on_message_received(self, msg: can.Message):
        """This method is called to handle the given message.
        :param msg:
            the delivered message
        """
        if self.should_rollover(msg):
            self.do_rollover()
            self.rollover_count += 1

        self.writer.on_message_received(msg)

    def get_new_writer(self, filename: StringPathLike):
        """Instantiate a new writer.
        :param filename:
            Path-like object that specifies the location and name of the log
            file.
            The log file format is defined by the suffix of `filename`.
        :return:
            An instance of a writer class.
        """
        suffix = pathlib.Path(filename).suffix.lower()
        try:
            writer_class = self.supported_writers[suffix]
        except KeyError:
            raise ValueError(
                f'Log format with suffix"{suffix}" is '
                f"not supported by {self.__class__.__name__}."
            )
        else:
            self._writer = writer_class(
                filename, *self.writer_args, **self.writer_kwargs
            )

    def stop(self):
        """Stop handling new messages.
        Carry out any final tasks to ensure
        data is persisted and cleanup any open resources.
        """
        self.writer.stop()

    @abstractmethod
    def should_rollover(self, msg: can.Message) -> bool:
        """Determine if the rollover conditions are met."""
        ...

    @abstractmethod
    def do_rollover(self):
        """Perform rollover."""
        ...


class SizedRotatingLogger(BaseRotatingLogger):
    """Log CAN messages to a sequence of files with a given maximum size.
    The logger creates a log file with the given `base_filename`. When the
    size threshold is reached the current log file is closed and renamed
    by adding a timestamp and the rollover count. A new log file is then
    created and written to.
    This behavior can be customized by setting the ´namer´ and `rotator`
    attribute.
    Example::
        from can import Notifier, SizedRotatingLogger
        from can.interfaces.vector import VectorBus
        bus = VectorBus(channel=[0], app_name="CANape", fd=True)
        logger = SizedRotatingLogger(
            base_filename="my_logfile.asc",
            max_bytes=5 * 1024 ** 2,  # =5MB
        )
        logger.rollover_count = 23  # start counter at 23
        notifier = Notifier(bus=bus, listeners=[logger])
    The SizedRotatingLogger currently supports the formats
      * .asc: :class:`can.ASCWriter`
      * .blf :class:`can.BLFWriter`
      * .csv: :class:`can.CSVWriter`
      * .log :class:`can.CanutilsLogWriter`
      * .txt :class:`can.Printer`
      * .n2k :class:'N2KWriter'
    The log files may be incomplete until `stop()` is called due to buffering.
    """

    def __init__(
        self, base_filename: StringPathLike,
        max_bytes: int = 0, *args, **kwargs
    ):
        """
        :param base_filename:
            A path-like object for the base filename. The log file format is
            defined by the suffix of `base_filename`.
        :param max_bytes:
            The size threshold at which a new log file shall be created.
            If set to 0, no rollover will be performed.
        """
        super(SizedRotatingLogger, self).__init__(*args, **kwargs)

        self.base_filename = os.path.abspath(base_filename)
        self.max_bytes = max_bytes

        self.get_new_writer(self.base_filename)

    def should_rollover(self, msg: can.Message) -> bool:
        if self.max_bytes <= 0:
            return False

        if self.writer.file.tell() >= self.max_bytes:
            return True

        return False

    def do_rollover(self):
        if self.writer:
            self.writer.stop()

        sfn = self.base_filename
        dfn = self.rotation_filename(self._default_name())
        self.rotate(sfn, dfn)

        self.get_new_writer(self.base_filename)

    def _default_name(self) -> StringPathLike:
        """Generate the default rotation filename."""
        path = pathlib.Path(self.base_filename)
        new_name = (
            path.stem
            + "_"
            + datetime.now().strftime("%Y-%m-%dT%H%M%S")
            + "_"
            + f"#{self.rollover_count:03}"
            + path.suffix
        )
        return str(path.parent / new_name)
