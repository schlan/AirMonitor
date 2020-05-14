#!/usr/bin/env python3

from time import sleep

# Sampling
OVER_SAMPLE_1 = 1
OVER_SAMPLE_2 = 2
OVER_SAMPLE_4 = 3
OVER_SAMPLE_8 = 4
OVER_SAMPLE_16 = 5

class BME280:
   
   class NotFoundException(Exception):
        pass

   _calib00    = 0x88

   _T1         = 0x88 - _calib00
   _T2         = 0x8A - _calib00
   _T3         = 0x8C - _calib00

   _P1         = 0x8E - _calib00
   _P2         = 0x90 - _calib00
   _P3         = 0x92 - _calib00
   _P4         = 0x94 - _calib00
   _P5         = 0x96 - _calib00
   _P6         = 0x98 - _calib00
   _P7         = 0x9A - _calib00
   _P8         = 0x9C - _calib00
   _P9         = 0x9E - _calib00

   _H1         = 0xA1 - _calib00

   _chip_id    = 0xD0
   _reset      = 0xE0

   _calib26    = 0xE1

   _H2         = 0xE1 - _calib26
   _H3         = 0xE3 - _calib26   
   _xE4        = 0xE4 - _calib26
   _xE5        = 0xE5 - _calib26
   _xE6        = 0xE6 - _calib26
   _H6         = 0xE7 - _calib26

   _ctrl_hum   = 0xF2
   _status     = 0xF3
   _ctrl_meas  = 0xF4
   _config     = 0xF5

   _rawdata    = 0xF7

   _p_msb      = 0xF7 - _rawdata
   _p_lsb      = 0xF8 - _rawdata
   _p_xlsb     = 0xF9 - _rawdata
   _t_msb      = 0xFA - _rawdata
   _t_lsb      = 0xFB - _rawdata
   _t_xlsb     = 0xFC - _rawdata
   _h_msb      = 0xFD - _rawdata
   _h_lsb      = 0xFE - _rawdata

   _os_ms = [0, 1, 2, 4, 8, 16]

   def __init__(self, i2c, addr, sampling=OVER_SAMPLE_1):
      self.i2c = i2c
      self.addr = addr
      self.sampling = sampling

      if not addr in i2c.scan():
         raise self.NotFoundException

      self._load_calibration()
      self.measure_delay = self._measurement_time(sampling, sampling, sampling)
      self.t_fine = 0.0

   def _measurement_time(self, os_temp, os_press, os_hum):
      ms = ( (1.25  + 2.3 * BME280._os_ms[os_temp]) +
             (0.575 + 2.3 * BME280._os_ms[os_press]) +
             (0.575 + 2.3 * BME280._os_ms[os_hum]) )
      return (ms/1000.0)

   def _u16(self, _calib, off):
      return (_calib[off] | (_calib[off+1]<<8))

   def _s16(self, _calib, off):
      v = self._u16(_calib, off)
      if v > 32767:
         v -= 65536
      return v

   def _u8(self, _calib, off):
      return _calib[off]

   def _s8(self, _calib, off):
      v = self._u8(_calib,off)
      if v > 127:
         v -= 256
      return v

   def _write_registers(self, data):
      self.i2c.write(self.addr, data)

   def _read_registers(self, reg, count):
      return self.i2c.read_block(self.addr, reg, n=count)     

   def _load_calibration(self):
      d1 = self._read_registers(BME280._calib00, 26)

      self.T1 = self._u16(d1, BME280._T1)
      self.T2 = self._s16(d1, BME280._T2)
      self.T3 = self._s16(d1, BME280._T3)

      self.P1 = self._u16(d1, BME280._P1)
      self.P2 = self._s16(d1, BME280._P2)
      self.P3 = self._s16(d1, BME280._P3)
      self.P4 = self._s16(d1, BME280._P4)
      self.P5 = self._s16(d1, BME280._P5)
      self.P6 = self._s16(d1, BME280._P6)
      self.P7 = self._s16(d1, BME280._P7)
      self.P8 = self._s16(d1, BME280._P8)
      self.P9 = self._s16(d1, BME280._P9)

      self.H1 = self._u8(d1, BME280._H1)

      d2 = self._read_registers(BME280._calib26, 7)

      self.H2 = self._s16(d2, BME280._H2)

      self.H3 = self._u8(d2, BME280._H3)

      t = self._u8(d2, BME280._xE5)

      t_l = t & 15
      t_h = (t >> 4) & 15

      self.H4 = (self._u8(d2, BME280._xE4) << 4) | t_l

      if self.H4 > 2047:
         self.H4 -= 4096

      self.H5 = (self._u8(d2, BME280._xE6) << 4) | t_h

      if self.H5 > 2047:
         self.H5 -= 4096

      self.H6 = self._s8(d2, BME280._H6)

   def _read_raw_data(self):

      # Set oversampling rate and force reading.

      self._write_registers(
         [BME280._ctrl_hum, self.sampling,
          BME280._ctrl_meas, self.sampling << 5 | self.sampling << 2 | 1])

      # Measurement delay.
      sleep(self.measure_delay)

      # Grab reading.
      d = self._read_registers(BME280._rawdata, 8)

      msb = self._u8(d, BME280._t_msb)
      lsb = self._u8(d, BME280._t_lsb)
      xlsb = self._u8(d, BME280._t_xlsb)
      raw_t = ((msb << 16) | (lsb << 8) | xlsb) >> 4

      msb = self._u8(d, BME280._p_msb)
      lsb = self._u8(d, BME280._p_lsb)
      xlsb = self._u8(d, BME280._p_xlsb)
      raw_p = ((msb << 16) | (lsb << 8) | xlsb) >> 4

      msb = self._u8(d, BME280._h_msb)
      lsb = self._u8(d, BME280._h_lsb)
      raw_h = (msb << 8) | lsb

      return raw_t, raw_p, raw_h

   def read_data(self):
      """
      Returns the temperature, pressure, and humidity as a tuple.

      Each value is a float.

      The temperature is returned in degrees centigrade.  The
      pressure is returned in Pascals.  The humidity is returned
      as the relative humidity between 0 and 100%.
      """

      raw_t, raw_p, raw_h = self._read_raw_data()

      var1 = (raw_t/16384.0 - (self.T1)/1024.0) * float(self.T2)
      var2 = (((raw_t)/131072.0 - (self.T1)/8192.0) *
              ((raw_t)/131072.0 - (self.T1)/8192.0)) * (self.T3)

      self.t_fine = var1 + var2

      t = (var1 + var2) / 5120.0

      var1 = (self.t_fine/2.0) - 64000.0
      var2 = var1 * var1 * self.P6 / 32768.0
      var2 = var2 + (var1 * self.P5 * 2.0)
      var2 = (var2/4.0)+(self.P4 * 65536.0)
      var1 = ((self.P3 * var1 * var1 / 524288.0) + (self.P2 * var1)) / 524288.0
      var1 = (1.0 + var1 / 32768.0)*self.P1
      if var1 != 0.0:
         p = 1048576.0 - raw_p
         p = (p - (var2 / 4096.0)) * 6250.0 / var1
         var1 = self.P9 * p * p / 2147483648.0
         var2 = p * self.P8 / 32768.0
         p = p + (var1 + var2 + self.P7) / 16.0
      else:
         p = 0

      h = self.t_fine - 76800.0

      h = ( (raw_h - ((self.H4) * 64.0 + (self.H5) / 16384.0 * h)) *
            ((self.H2) / 65536.0 * (1.0 + (self.H6) / 67108864.0 * h *
            (1.0 + (self.H3) / 67108864.0 * h))))

      h = h * (1.0 - self.H1 * h / 524288.0)

      if h > 100.0:
         h = 100.0
      elif h < 0.0:
         h = 0.0

      return t, p, h