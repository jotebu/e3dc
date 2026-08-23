<?php

declare(strict_types=1);

/*
 * E3DC IP-Symcon module v2.0 bootstrap
 *
 * Target: E3/DC Simple Mode V2.00 / S20 generation
 *
 * The original v1.6 implementation is intentionally kept unchanged in
 * module_legacy.php. Constants are defined here before loading the legacy
 * implementation, because the legacy module uses these constants to build
 * its configuration form and Modbus instances dynamically.
 *
 * Simple Mode V2.00 extends the power-meter block from register 40105 up to
 * 40184 (20 power meters, IDs 0..19). The existing implementation already
 * calculates the register addresses dynamically; raising E3DC_POWERMETER is
 * therefore sufficient for this register block.
 */

if (!defined('E3DC_WALLBOX')) {
    define('E3DC_WALLBOX', 8);
}
if (!defined('E3DC_POWERMETER')) {
    define('E3DC_POWERMETER', 20);
}
if (!defined('E3DC_INVERTER')) {
    define('E3DC_INVERTER', 8);
}
if (!defined('E3DC_MPPT')) {
    define('E3DC_MPPT', 3);
}

require_once __DIR__ . '/module_legacy.php';
