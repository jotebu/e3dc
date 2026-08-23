#!/usr/bin/env python3
from pathlib import Path

path = Path('e3dc/module_legacy.php')
s = path.read_text(encoding='utf-8')
original = s

# 1) S20/V2 branch: register 40137 must never be created as SG Ready.
old_sg = '''\t\t\t\tif (!defined('E3DC_SIMPLE_MODE_V2') || !E3DC_SIMPLE_MODE_V2)\n\t\t\t\t{\n\t\t\t\t\t$inverterModelRegister_array[] = array(40137, 1, 3, "SG Ready-Status", "Uint16", "enumerated_sg-ready-status", "SG Ready-Status:\n- Betriebszustand 1 (Sperrbetrieb):Dieser Betriebszustand ist abwärtskompatibel zur häufig zufesten Uhrzeiten geschalteten EVU-Sperre und umfasstmaximal 2 Stunden „harte“ Sperrzeit.\n- Betriebszustand 2 (Normalbetrieb):In dieser Schaltung läuft die Wärmepumpe imenergieeffizienten Normalbetrieb mit anteiligerWärmespeicher-Füllung für die maximal zweistündige EVU-Sperre.\n- Betriebszustand 3 (PV-Überschussbetrieb): In diesem Betriebszustand läuft die Wärmepumpe innerhalb des Reglers im verstärkten Betrieb für Raumheizung und Warmwasserbereitung. Es handelt sich dabei nicht um einen definitiven Anlaufbefehl, sondern um eine Einschaltempfehlung entsprechend der heutigen Anhebung.\n- Betriebszustand 4 (Betrieb für Abregelung): Hierbei handelt es sich um einen definitiven Anlaufbefehl, insofern dieser im Rahmen der Regeleinstellungen möglich ist.");\n\t\t\t\t}\n'''
if s.count(old_sg) != 1:
    raise SystemExit(f'ABBRUCH: SG-Ready-V2-Block erwartet 1x, gefunden {s.count(old_sg)}x')
s = s.replace(old_sg, '', 1)

# 2) Convert/remove a stale 40137 SG-Ready instance safely.
old_migration = '''\t\t\t\t// Simple Mode V2.00: Register 40137 is the type register of Powermeter 8.\n\t\t\t\t// Remove a stale SG-Ready instance created by an older module version.\n\t\t\t\tif (defined('E3DC_SIMPLE_MODE_V2') && E3DC_SIMPLE_MODE_V2)\n\t\t\t\t{\n\t\t\t\t\t$legacySgReadyId = @IPS_GetObjectIDByIdent("40137", $categoryId);\n\t\t\t\t\tif (false !== $legacySgReadyId && "SG Ready-Status" == IPS_GetName($legacySgReadyId))\n\t\t\t\t\t{\n\t\t\t\t\t\t$this->deleteInstanceRecursive($legacySgReadyId);\n\t\t\t\t\t}\n\t\t\t\t}\n'''
new_migration = '''\t\t\t\t// S20 / Simple Mode V2.00: register 40137 belongs to Powermeter 8.\n\t\t\t\t// Convert an existing legacy SG-Ready value if Powermeter 8 is enabled;\n\t\t\t\t// otherwise remove the stale Modbus instance.\n\t\t\t\t$legacySgReadyId = @IPS_GetObjectIDByIdent("40137", $categoryId);\n\t\t\t\tif (false !== $legacySgReadyId)\n\t\t\t\t{\n\t\t\t\t\t$legacySgReadyValueId = @IPS_GetObjectIDByIdent("Value", $legacySgReadyId);\n\t\t\t\t\tif (false !== $legacySgReadyValueId\n\t\t\t\t\t\t&& MODUL_PREFIX.".SG-Ready-Status.Int" == IPS_GetVariable($legacySgReadyValueId)['VariableCustomProfile'])\n\t\t\t\t\t{\n\t\t\t\t\t\tif (isset($readPowermeter[8]) && $readPowermeter[8])\n\t\t\t\t\t\t{\n\t\t\t\t\t\t\tIPS_SetVariableCustomProfile($legacySgReadyValueId, MODUL_PREFIX.".Powermeter.Int");\n\t\t\t\t\t\t}\n\t\t\t\t\t\telse\n\t\t\t\t\t\t{\n\t\t\t\t\t\t\t$this->deleteInstanceRecursive($legacySgReadyId);\n\t\t\t\t\t\t}\n\t\t\t\t\t}\n\t\t\t\t}\n'''
if s.count(old_migration) != 1:
    raise SystemExit(f'ABBRUCH: alter 40137-Migrationsblock erwartet 1x, gefunden {s.count(old_migration)}x')
s = s.replace(old_migration, new_migration, 1)

# 3) Apply ByteOrder=3 explicitly in this S20 branch, without the failing runtime guard.
old_byte = '''\t\t\t\t\t// S20 / Simple Mode V2.00: verified on S20 X PRO H20_2026_02.\n\t\t\t\t\t// IP-Symcon ByteOrder 3 = Little Endian (Byte Swap).\n\t\t\t\t\tif (defined('E3DC_SIMPLE_MODE_V2') && E3DC_SIMPLE_MODE_V2\n\t\t\t\t\t\t&& in_array($inverterModelRegister[IMR_START_REGISTER], array(40068, 40070, 40072, 40074, 40076, 40078, 40080), true)\n\t\t\t\t\t\t&& 3 != IPS_GetProperty($instanceId, "ByteOrder"))\n\t\t\t\t\t{\n\t\t\t\t\t\tIPS_SetProperty($instanceId, "ByteOrder", 3);\n\t\t\t\t\t}\n'''
new_byte = '''\t\t\t\t\t// S20 / Simple Mode V2.00: verified on S20 X PRO H20_2026_02.\n\t\t\t\t\t// IP-Symcon ByteOrder 3 = Little Endian (Byte Swap).\n\t\t\t\t\tif (in_array($inverterModelRegister[IMR_START_REGISTER], array(40068, 40070, 40072, 40074, 40076, 40078, 40080), true)\n\t\t\t\t\t\t&& 3 != IPS_GetProperty($instanceId, "ByteOrder"))\n\t\t\t\t\t{\n\t\t\t\t\t\tIPS_SetProperty($instanceId, "ByteOrder", 3);\n\t\t\t\t\t\t$this->SendDebug("S20 ByteOrder", "REG_".$inverterModelRegister[IMR_START_REGISTER]." -> ByteOrder 3", 0);\n\t\t\t\t\t}\n'''
if s.count(old_byte) != 1:
    raise SystemExit(f'ABBRUCH: ByteOrder-V2-Block erwartet 1x, gefunden {s.count(old_byte)}x')
s = s.replace(old_byte, new_byte, 1)

if s == original:
    raise SystemExit('ABBRUCH: Keine Aenderung erzeugt')

path.write_text(s, encoding='utf-8')
print('OK: S20-V2-Fix2 exakt angewendet.')
