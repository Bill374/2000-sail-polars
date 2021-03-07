#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  5 18:52:25 2021

@author: wmorland
"""

import can
from datetime import datetime
import pathlib
from typing import Optional
from can.typechecking import StringPathLike


class N2KWriter(can.BaseIOHandler, can.Listener):
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
        PRIORITY =  0b11100_00000000_00000000_00000000
        PDU_F =     0b00000_11111111_00000000_00000000
        PDU_S =     0b00000_00000000_11111111_00000000
        SHORT_PGN = 0b00011_11111111_00000000_00000000
        LONG_PGN =  0b00011_11111111_11111111_00000000
        SOURCE =    0b00000_00000000_00000000_11111111

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

        row = ','.join([
            datetime.fromtimestamp(msg.timestamp).strftime('%Y-%m-%dT%H:%M:%SZ'),
            str(priority),
            str(pgn),
            str(source),
            str(destination),
            str(msg.dlc),
        ])
        dlc = msg.dlc
        data = msg.data
        while dlc:
            row = ','.join([row, format(data & 0xFF, 'x')])
            data >> 8
            dlc -= 1
        self.file.write(row)
        self.file.write('\n')


class Logger(can.BaseIOHandler, can.Listener):
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
                    for writer in can.iter_entry_points("can.io.message_writer")
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

