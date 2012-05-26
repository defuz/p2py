<?php
/**
 * Copyright (c) 2009, PHPServer
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *     * Redistributions of source code must retain the above copyright
 *       notice, this list of conditions and the following disclaimer.
 *     * Redistributions in binary form must reproduce the above copyright
 *       notice, this list of conditions and the following disclaimer in the
 *       documentation and/or other materials provided with the distribution.
 *     * Neither the name of the Cesar Rodas nor the
 *       names of its contributors may be used to endorse or promote products
 *       derived from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY CESAR RODAS ''AS IS'' AND ANY
 * EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL CESAR RODAS BE LIABLE FOR ANY
 * DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * @package Core-Instruments
 * @subpackage kernel
 * @author Cesar Rodas, Marat Ibadinov
 */
/**
 * @package Core-Instruments
 * @subpackage kernel
 * @author Cesar Rodas, Marat Ibadinov
 */
class SerializerException extends GenericException {

    const STRING_SIZE   = 1;
    const ARRAY_SIZE    = 2;
    const OBJECT_SIZE   = 3;
    const UNKNOWN_TYPE  = 4;

    static public $messages = array(
        self::STRING_SIZE   => 'Failed to obtain string size',
        self::ARRAY_SIZE    => 'Failed to obtain array size',
        self::OBJECT_SIZE   => 'Failed to obtain object size',
        self::UNKNOWN_TYPE  => 'Unknown type: 0x%s',
    );

    public function __construct($code, $val = NULL) {
        $message = isset($val) ? sprintf(self::$messages[$code], $val) : self::$messages[$code];
        parent::__construct($message, $code, NULL);
    }

}

/**
 * @package Core-Instruments
 * @subpackage kernel
 * @author Cesar Rodas, Marat Ibadinov
 */
class serializer {

    const T_ZERO = 0x01;
    const T_NULL = 0x02;

    /* integers */
    const T_1INT_POS = 0x10;
    const T_1INT_NEG = 0x11;
    const T_2INT_POS = 0x12;
    const T_2INT_NEG = 0x13;
    const T_4INT_POS = 0x14;
    const T_4INT_NEG = 0x15;

    /* floats  */
    const T_FLOAT_POS = 0x20;
    const T_FLOAT_NEG = 0x21;

    /* boolean */
    const T_BOOL_TRUE = 0x30;
    const T_BOOL_FALSE = 0x31;

    /* array */
    const T_ARRAY = 0x40;

    /* object */
    const T_OBJECT = 0x50;

    /* string */
    const T_STRING = 0x60;

    static public function unserialize(&$var) {
        $i = 0;
        return self::unserializePart($var, false, $i);
    }

    static public function serialize($var) {
        $str = "";
        if (is_integer($var) && $var == 0) {
            return chr(self::T_ZERO);
        }
        switch (($type = gettype($var))) {
            case "NULL":
                return chr(self::T_NULL);
            case "string":
                $str .= chr(self::T_STRING);
                $str .= self::serialize((int) strlen($var));
                $str .= $var;
                break;
            case "float":
            case "double":
                $str .= chr($var > 0 ? self::T_FLOAT_POS : self::T_FLOAT_NEG);
                $str .= self::fromfloat($var);
                break;
            case "integer":
            case "numeric":
                $t = abs($var);
                if ($t < 255) {
                    $str .= chr($var > 0 ? self::T_1INT_POS : self::T_1INT_NEG);
                    $str .= chr($t);
                } else if ($t < 65536) {
                    $str .= chr($var > 0 ? self::T_2INT_POS : self::T_2INT_NEG);
                    $str .= self::fromint($var, 2);
                } else {
                    $str .= chr($var > 0 ? self::T_4INT_POS : self::T_4INT_NEG);
                    $str .= self::fromint($var);
                }
                break;
            case "boolean":
                $str .= chr($var ? self::T_BOOL_TRUE : self::T_BOOL_FALSE);
                break;
            case "array":
                $str .= chr(self::T_ARRAY);
                $tmp = "";
                foreach ($var as $key => $value) {
                    $tmp .= self::serialize($key);
                    $tmp .= self::serialize($value);
                }
                $str .= self::serialize(strlen($tmp));
                $str .= $tmp;
                break;
            case "object":
                $str .= chr(self::T_OBJECT);
                $str .= self::serialize(get_class($var));
                $tmp = "";
                foreach (get_object_vars($var) as $key => $value) {
                    $tmp .= self::serialize($key);
                    $tmp .= self::serialize($value);
                }
                $str .= self::serialize(strlen($tmp));
                $str .= $tmp;
                break;
            default:
                throw new SerializerException(SerializerException::UNKNOWN_TYPE, dechex($type));
                break;
        }
        return $str;
    }

    static private function unserializePart(&$var, $just_first = false, &$start) {
        $len = strlen($var);
        $out = NULL;
        for ($i = &$start; $i < $len; $i++) {
            $type = ord($var[$i++]);
            switch ($type) {
                case self::T_NULL:
                    return NULL;
                case self::T_ZERO:
                    $out = 0;
                    break;
                case self::T_1INT_POS:
                case self::T_1INT_NEG:
                    $out = ord($var[$i]);
                    if ($type == self::T_1INT_NEG)
                        $out *= -1;
                    $i++;
                    break;
                case self::T_2INT_POS:
                case self::T_2INT_NEG:
                    $out = self::toint(substr($var, $i, 2), 2);
                    if ($type == self::T_2INT_NEG)
                        $out *= -1;
                    $i += 2;
                    break;
                case self::T_4INT_POS:
                case self::T_4INT_NEG:
                    $out = self::toint(substr($var, $i, 4), 4);
                    if ($type == self::T_4INT_NEG)
                        $out *= -1;
                    $i += 4;
                    break;
                case self::T_FLOAT_POS:
                case self::T_FLOAT_NEG:
                    $out = self::tofloat(substr($var, $i, 6));
                    if ($type == self::T_FLOAT_NEG)
                        $out *= -1;
                    $i += 6;
                    break;
                case self::T_BOOL_TRUE:
                    $out = true;
                    break;
                case self::T_BOOL_FALSE:
                    $out = false;
                    break;
                case self::T_STRING:
                    $xlen = self::unserializePart($var, true, $i);
                    if (!is_numeric($xlen)) {
                        throw new SerializerException(SerializerException::STRING_SIZE);
                    }
                    $out = substr($var, $i, $xlen);
                    $i += $xlen;
                    break;
                case self::T_ARRAY:
                    $xlen = self::unserializePart($var, true, $i);
                    if (!is_numeric($xlen)) {
                        throw new SerializerException(SerializerException::ARRAY_SIZE);
                    }
                    $out = array();
                    $tmp = substr($var, $i, $xlen);
                    $itmp = 0;
                    while ($itmp < $xlen) {
                        $key = self::unserializePart($tmp, true, $itmp);
                        $value = self::unserializePart($tmp, true, $itmp);
                        $out[$key] = $value;
                    }
                    $i += $xlen;
                    break;
                case self::T_OBJECT:
                    $class_name = self::unserializePart($var, true, $i);
                    $xlen = self::unserializePart($var, true, $i);
                    if (!is_numeric($xlen)) {
                        throw new SerializerException(SerializerException::OBJECT_SIZE);
                    }
                    /**/
                    $class_name = class_exists($class_name) ? $class_name : 'stdClass';
                    $out = new $class_name;
                    /**/
                    $tmp = substr($var, $i, $xlen);
                    $itmp = 0;
                    while ($itmp < $xlen) {
                        $key = self::unserializePart($tmp, true, $itmp);
                        $value = self::unserializePart($tmp, true, $itmp);
                        $out->$key = $value;
                    }
                    $i += $xlen;

                    break;
                default:
                    throw new SerializerException(SerializerException::UNKNOWN_TYPE, dechex($type));
            }
            if (!is_NULL($out)) {
                break;
            }
        }
        return $out;
    }

    static private function toint($string, $blen = 4) {
        $out = 0;
        $n = ($blen - 1) * 8;
        for ($bits = 0; $bits < $blen; $bits++) {
            $out |= ord($string[$bits]) << $n;
            $n -= 8;
        }
        return $out;
    }

    static private function fromint($int, $blen = 4) {
        $int = (int) ($int < 0) ? (-1 * $int) : $int;
        $bytes = str_repeat(" ", $blen);
        $n = ($blen - 1) * 8;
        for ($bits = 0; $bits < $blen; $bits++) {
            $bytes[$bits] = chr($int >> $n);
            $int -= $bytes[$bits] << $n;
            $n -= 8;
        }
        return $bytes;
    }

    static private function fromfloat($float) {
        $str = self::fromint($float);
        $str .= self::fromint(round(($float - (int) $float) * 1000), 2);
        return $str;
    }

    static private function tofloat($string) {
        $float = self::toint(substr($string, 0, 4));
        $float += self::toint(substr($string, 4, 2), 2) / 1000;
        return $float;
    }

}

?>