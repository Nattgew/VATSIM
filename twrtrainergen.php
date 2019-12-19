<?php

ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

include_once 'logdbconfig.php';
//TODO: Database with airport locations
include_once 'locdbconfig.php';
?>
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>TWRTrainer Generator</title>
<meta name="description" content="TWRTrainer Generator">
<meta name="author" content="N">
<link rel="stylesheet" href="style.css">
<style>
/*https://www.w3schools.com/howto/howto_css_tooltip.asp*/
 /* Tooltip container */
.tooltip {
  position: relative;
  display: inline-block;
  /*background: #f99;*/
  border-bottom: 1px dotted black; /* If you want dots under the hoverable text */
}

/* Tooltip text */
.tooltip .tooltiptext {
  visibility: hidden;
  width: 120px;
  background-color: #555;
  color: #fff;
  text-align: center;
  padding: 5px 0;
  border-radius: 6px;

  /* Position the tooltip text */
  position: absolute;
  z-index: 1;
  bottom: 125%;
  left: 50%;
  margin-left: -60px;

  /* Fade in tooltip */
  opacity: 0;
  transition: opacity 0.3s;
}

/* Tooltip arrow */
.tooltip .tooltiptext::after {
  content: "";
  position: absolute;
  top: 100%;
  left: 50%;
  margin-left: -5px;
  border-width: 5px;
  border-style: solid;
  border-color: #555 transparent transparent transparent;
}

/* Show the tooltip text when you mouse over the tooltip container */
.tooltip:hover .tooltiptext {
  visibility: visible;
  opacity: 1;
  /*transition: opacity 0.3s;*/
}

.flighttable td {
	padding:4px;
}

.tdm {
  background: #f99;
}

.tdv {
  background: #fc6;
}
</style>
</head>
<body>

<?php

//https://www.php.net/manual/en/function.array-unique.php#116302
function unique_multidim_array($array, $key) {
  $temp_array = array();
  $i = 0;
  $key_array = array();
  #echo "\nMultidim length: ".count($array)."\n";
  foreach($array as $val) {
    //echo $i;
    #echo var_dump($val);
    #echo $val[0];
    if (!in_array($val[$key], $key_array)) {
      $key_array[] = $val[$key];
      $temp_array[] = $val;
    }
    //$i++;
  }
  return $temp_array;
}

//https://www.php.net/manual/en/function.explode.php#111307
function multiexplode ($delimiters,$string) {
  $ready = str_replace($delimiters, $delimiters[0], $string);
  $launch = explode($delimiters[0], $ready);
  return  $launch;
}

function cmp(array $a, array $b) {
  if ($a[1] < $b[1]) {
    return -1;
  } else if ($a[1] > $b[1]) {
    return 1;
  } else {
    return 0;
  }
}

if( $_GET["icao"] ) {
	$icao = $_GET['icao'];
} else {
	$icao = "Invalid ICAO";
}

function makeairfile(array $acs, int $felev, string $outfile) {
  // LOAD FILE HERE
  foreach ($acs as &$ac) {
    $fpline = fptoline($ac[0], $felev);
    //write $fpline;
  }
}

function fptoline(array $ac, int $felev) {
  #echo "<p>".var_dump($ac)."</p>";
  $type = splittype($ac[0]['planned_aircraft'])[1];
}

function getrndsq() {
  $sq = "";
  while (in_array($sq, array("", "7500", "7600", "7700"))) {
    for ($i=0; $i<4; $i++) {
      $sq .= (string) rand(0,7);
    }
  }
  return $sq;
}

function getrndmode() {
  if (rand(0,1) == 1) {
    $mode = "N";
  } else {
    $mode = "S";
  }
  return $mode;
}

function getfplist(string $icao) {
  global $conn;
  $sql = "SELECT * FROM `flights` WHERE planned_depairport = ?";
  $stmt = $conn->prepare($sql);
  $stmt->bind_param("s", $icao);
  $stmt->execute();
  $result = $stmt->get_result();

  $fps = array();

  if ($result->num_rows > 0) {
    // output data of each row
    while($row = $result->fetch_assoc()) {
      $csign = $row["callsign"];
      $actype = $row["planned_aircraft"];
      $dest = $row["planned_destairport"];
      $alt = $row["planned_altitude"];
      $rules = $row["planned_flighttype"];
      $rmks = $row["planned_remarks"];
      $route = $row["planned_route"];
      $logon = $row["time_logon"];
      $apt = $row["planned_depairport"];
      $fps[] = array("callsign" => $csign, "planned_aircraft" => $actype,
                     "planned_destairport" => $dest, "planned_altitude" => $alt,
                     "planned_flighttype" => $rules, "planned_remarks" => $rmks,
                     "planned_route" => $route, "time_logon" => $logon,
                     "planned_depairport" => $apt);
    }
  } else {
    echo "Could not find any flight plans!";
  }
  return $fps;
}

function randomfp(string $airport) {
  $fplist = getfplist($airport);
  return array_rand($fplist);
}

function alt_to_int(string $altstr) {
  if (substr($altstr,0,2) == "FL") {
    #echo "FL like a normal person\n";
    $alt = (int) substr($altstr,2)."00";
  } elseif (substr($altstr,0,1) == "F") {
    #echo "F like a weird person\n";
    $alt = (int) substr($altstr,1)."00";
  } else {
    try {
      $alt = (int) $altstr;
      if ($alt < 1000) {
        $alt *= 100;
      }
      #echo "number like acceptable person\n";
    } catch (Exception $e) {
      #echo "Could not determine altitude: ".$altstr."\n";
      $alt = (int) 0;
    }
  }
  #echo "ALT: ".$altstr." -> ".strval($alt)."<br/>";
  return $alt;
}

function int_to_FL(int $alt) {
  if ($alt >= 10000) {
    $flightlevel = "FL".substr(strval($alt),0,3);
  } elseif ($alt >= 1000) {
    $flightlevel = "FL0".substr(strval($alt),0,2);
    #echo "Some moron filed ".strval($alt);
  } else {
    $flightlevel = "FL00".substr(strval($alt),0,1);
    #echo "Some moron filed ".strval($alt)."<br/>";
  }
  return $flightlevel;
}

function manglealt(string $alt) {
  $altnum = alt_to_int($alt);
  if (rand(0,1) == 1) {
    $roll = 1;
  } else {
    $roll = -1;
  }
  $newalt = (string) $altnum+1000*$roll;
  return $newalt;
}

function mangleroute(string $airport, string $route) {
  // ADD WAY TO ADJUST THESE
  $chance_swap = 0.1;
  $chance_dct = 0.05;
  $chance_blk = 0.05;

  $mangletype = array(0, $route);
  $newplan = randomfp($airport);
  $newroute = $newplan['planned_route'];
  if (rand(0,100) < $chance_swap*100) {
  } elseif (rand(0,100) < $chance_dct*100) {
    $newroute = "DCT";
  } elseif (rand(0,100) < $chance_blk*100) {
    $newroute = "";
  } else {
    $origpoints = multiexplode(array(" ","|","."),$route);
    $newpoints = multiexplode(array(" ","|","."), $newroute);
    $elemstoswap = rand(1,4);
    $mangledpoints = array_merge(array_slice($origpoints, 0, $elemstoswap), array_slice($newpoints, $elemstoswap));
    $newroute = implode(" ", $mangledpoints);
    $mangletype = array($elemstoswap, $route);
  }
  return array($newroute, $mangletype);
}

function mangledest(string $dest) {
  $first = substr($dest, 1);
  $last = str_shuffle(substr($dest, 2));
  $shuffled = $first . $last;
  return $shuffled;
}

function rndeqpcode() {
  $validcodes = array('H', 'W', 'Z', 'L', 'X', 'T', 'U', 'D', 'B', 'A', 'M', 'N', 'P', 'Y', 'C', 'I', 'V', 'S', 'G');
  if (rand(1,10) > 1) {
    $thiscode = "";
  } else {
    $thiscode = "/" . array_rand($validcodes);
  }
  return $thiscode;
}

function splittype(string $type) {
  $fields = explode('/', $type);
  $wt = "";
  $ec = "";
  if (strlen($fields[0]) == 1) {
    if (count($fields) > 1) {
      $wt = $fields[0];
      $type = $fields[1];
      if (count($fields) > 2) {
        $ec = $fields[2];
      }
    } else {
      $type = $fields[0];
    }
  } else {
    $type = $fields[0];
    if (count($fields) > 1) {
      $ec = $fields[1];
    }
  }
  return array($wt, $type, $ec);
}

function mangleec(string $type) {
  $typefields = splittype($type);
  $wt = $typefields[0];
  $newwt = $wt;
  if ($wt != "") {
    if (rand(0,1) == 1) {
      if ($wt == "T") {
        $newwt = "H/";
      } elseif ($wt == "H") {
        if (rand(0,1) == 1) {
          $newwt = "";
        } else {
          $newwt = "T/";
        }
      }
    } else {
      $newwt = $wt . "/";
    }
  } else {
    if (rand(0,1) == 1) {
      if (rand(0,1) == 1) {
        $newwt = "T/";
      } else {
        $newwt = "H/";
      }
    }
  }
  $newec = rndeqpcode();
  $newtype = $newwt . $typefields[1] . $newec;
  return $newtype;
}
#keys = ["callsign", "cid", "realname", "clienttype", "frequency", "latitude", "longitude", "altitude", "groundspeed", "planned_aircraft", "planned_tascruise", "planned_depairport", "planned_altitude", "planned_destairport", "server", "protrevision", "rating", "transponder", "facilitytype", "visualrange", "planned_revision", "planned_flighttype", "planned_deptime", "planned_actdeptime", "planned_hrsenroute", "planned_minenroute", "planned_hrsfuel", "planned_minfuel", "planned_altairport", "planned_remarks", "planned_route", "planned_depairport_lat", "planned_depairport_lon", "planned_destairport_lat", "planned_destairport_lon", "atis_message", "time_last_atis_received", "time_logon", "heading", "QNH_iHg", "QNH_Mb"]

function manglerules(string $rules) {
  if ( $rules == "I" ) {
    $rules = "V";
  } else {
    $rules = "I";
  }
  if (rand(0,100) < 2 ) {
    $rules = "S";
  }
  return $rules;
}

function manglefp(array $fp, string $focus = "None") {
  // ADD WAY TO ADJUST THESE
  if ($focus == "TWR") {
    $chance_ec = 0.01;
    $chance_alt = 0.01;
    $chance_dest = 0.001;
    $chance_route = 0.01;
    $chance_rules = 0.01;
  } else {
    $chance_ec = 0.5;
    $chance_alt = 0.25;
    $chance_dest = 0.01;
    $chance_route = 0.25;
    $chance_rules = 0.1;
  }
  //Could also store the mangles themselves here
  //type, alt, dest, route, rules
  $mangled = array_fill(0, 5, "");
  if (rand(0,100) < $chance_ec * 100) {
    //TODO: specify which parts have been broken
    $mangled[0] = $fp['planned_aircraft'];
    $fp['planned_aircraft'] = mangleec($fp['planned_aircraft']);
  }
  if (rand(0,100) < $chance_alt * 100) {
    $mangled[1] = $fp['planned_altitude'];
    $fp['planned_altitude'] = manglealt($fp['planned_altitude']);
  }
  if (rand(0,100) < $chance_dest * 100) {
    $mangled[2] = $fp['planned_destairport'];
    $fp['planned_destairport'] = mangledest($fp['planned_destairport']);
  }
  if (rand(0,100) < $chance_route * 100) {
    //$mangled[3] = $fp['planned_route'];
    $mreturn = mangleroute($fp['planned_depairport'], $fp['planned_route']);
    $fp['planned_route'] = $mreturn[0];
    $mangled[3] = $mreturn[1];
  }
  if (rand(0,100) < $chance_rules * 100) {
    $mangled[4] = $fp['planned_flighttype'];
    $fp['planned_flighttype'] = manglerules($fp['planned_flighttype']);
  }
  return array($fp, $mangled);
}

function getlocations(array $fp) {
  global $conn;
  $coords = array();
  $sql = 'SELECT latitude, longitude FROM flights WHERE callsign = ? AND time_logon = ? AND groundspeed = "0"';
  if ($stmt = $conn->prepare($sql)) {
    $stmt->bind_param("ss", $fp['callsign'], $fp['time_logon']);
    $stmt->execute();

    $result = $stmt->get_result();

    if($result->num_rows > 0) {
      while ($loc = $result->fetch_assoc()) {
        #echo "<p>".var_dump($loc)."</p>";
        $coords[] = array((float)$loc['latitude'],(float)$loc['longitude']);
      }
    }
    //$stmt->close();
  } else {
    echo "<p>Failed to prepare statement for ".$fp['callsign']."</p>";
    $error = $conn->errno . ' ' . $conn->error;
    echo $error; // 1054 Unknown column 'foo' in 'field list'
  }
  return $coords;
}

function usespot(array $fp, array $spots) {
  $spotmatch = "";
  $coords = getlocations($fp);
  foreach ($coords as &$loc) {
    $dists = array();
    foreach ($spots as &$spot) {
      $dists[] = array($spot, cosinedist($loc, $spot[1]));
    }
    usort($dists, 'cmp');
    if ($dists[0][1] < 200/6076) {
      echo "<p>Matching original spot ".$dists[0][0][0]."</p>";
      $spotmatch = $dists[0][0];
      break;
    } else {
      if ($dists[0][1] < 0.5) {
        $dstr = (string) round($dists[0][1]*6076) . "ft";
      } else {
        $dstr = (string) round($dists[0][1]) . "nmi";
      }
      echo "<p>Closest spot ".$dists[0][0][0]." was ".$dstr." away</p>";
    }
  }
  return $spotmatch;
}

function cosinedist(array $latlon1, array $latlon2) {
  #echo "Dist from ".var_dump($latlon1)." to ".var_dump($latlon2)."</p>";
  $lat1 = $latlon1[0];
  $lon1 = $latlon1[1];
  $lat2 = $latlon2[0];
  $lon2 = $latlon2[1];
  $phi1 = deg2rad($lat1);
  $phi2 = deg2rad($lat2);
  $dellamb = deg2rad($lon2-$lon1);
  $R = 3440.06479; // Nmi
  $d = acos(sin($phi1)*sin($phi2) + cos($phi1)*cos($phi2) * cos($dellamb)) * $R;
  return $d;
}

function inithdg($latlon1,$latlon2) { #Find heading between coordinates
  $phi1 = deg2rad($latlon1[0]);
  $phi2 = deg2rad($latlon2[0]);
  $lamb1 = deg2rad($latlon1[1]);
  $lamb2 = deg2rad($latlon2[1]);
  $y = sin($lamb2-$lamb1) * cos($phi2);
  $x = cos($phi1)*sin($phi2) - sin($phi1)*cos($phi2)*cos($lamb2-$lamb1);
  $brng = rad2deg(atan2($y, $x));
  if ($brng<0) {
    $brng = $brng + 360;
  }
  return $brng;
}

function aptcoords($icao) {
  global $conn_l;
  $sql = "SELECT lat, lon FROM airports WHERE icao = ?";
  if ($stmt = $conn_l->prepare($sql)) {
    #echo "<p>".var_dump($conn_l->error_list)."</p>";
    $stmt->bind_param("s", $icao);
    $stmt->execute();
    $result = $stmt->get_result();

    $coords = array();

    if($result->num_rows > 0) {
      while ($loc = $result->fetch_assoc()) {
        $coords = array((float)$loc['lat'],(float)$loc['lon']);
      }
    }
  } else {
    $error = $conn_l->errno . ' ' . $conn_l->error;
    echo $error; // 1054 Unknown column 'foo' in 'field list'
  }
  return $coords;
}

//Read apt file to get parking spots
$parkingspots = array();
$gaspots = array();
$cargospots = array();
$milspots = array();
$otherspots = array();

$myfile = fopen("twrtrainer/".$icao.".apt", "r") or die("Unable to open file!");

$name = "";
$magvar = 0;
$fieldelev = "0";
while(! feof($myfile)) {
  $line = fgets($myfile);
  if ($name <> "") {
    $coords = explode(" ",$line);
    $parkingspots[] = array($name, $coords);
  }
  if (substr($line,0,9) == "[PARKING ") {
    $name = substr($line, 9, -2);
  } else {
    $name = "";
    if (substr($line,0,18) == "magnetic variation=" ) {
      $magvar = (int)substr($line,19);
    } elseif (substr($line,0,15) == "field elevation=" ) {
      $fieldelev = substr($line,16);
    }
  }
}

fclose($myfile);

echo "<p>Found ".count($parkingspots)." parking spots";

foreach ($parkingspots as &$spot) {
  if (strpos($spot[0], "GA") !== false) {
    $gaspots[] = $spot;
  } elseif (strpos($spot[0], "CARGO") !== false) {
    $cargospots[] = $spot;
  } elseif (strpos($spot[0], "ANG") !== false) {
    $milspots[] = $spot;
  } else {
    $otherspots[] = $spot;
  }
}

echo " GA: ".count($gaspots)."   CG: ".count($cargospots)."   MI: ".count($milspots)."   TR: ".count($otherspots)."</p>";

shuffle($gaspots);
shuffle($cargospots);
shuffle($milspots);
shuffle($otherspots);

//$sql = "SHOW COLUMNS FROM flights";
//$result = $conn->query($sql);

$fps = getfplist($icao);

echo "<p>Found ".count($fps)." flight plans.</p>";
shuffle($fps);

// foreach ($fps as $fp) {
//   foreach ($fp as $elem) {
//     echo strval($elem)."<br/>";
//   }
// }

$flightplans = unique_multidim_array($fps, "callsign");

# Keep track of recently used spots
$usedspots = array();

# Airlines to put on cargo ramps
$cargoairlines = array("FDX", "UPS", "GEC", "GTI", "ATI", "DHL", "BOX", "CLX", "ABW", "SQC", "ABX", "AEG", "AJT", "CLU", "BDA", "DAE", "DHK", "JOS", "RTM", "DHX", "BCS", "CKS", "MPH", "NCA", "PAC", "TAY", "RCF", "CAO", "TPA", "CKK", "MSX", "LCO", "SHQ", "LTG", "ADB");

# For aircraft not listed, would rather have GA at term than airliner at GA
$gaaircraft = array("C172", "C182", "PC12", "C208", "PA28", "BE35", "B350", "FA20", "C750", "CL30", "C25", "BE58", "BE9L", "HAWK", "C150", "P06T", "H25B", "TBM7", "P28U", "BE33", "AC11", "DHC6", "EA50", "SF50", "C510", "M7", "DC3", "UH1", "E55P", "TBM9", "PC21", "C25A", "B58T", "H850", "BE20", "DA42", "S76", "Z50", "A139", "C206", "AC50", "EPIC", "LJ45", "LJ60", "C404", "FA50", "C170", "GLF5", "C210", "FA7X", "DA62", "DR40", "P28A", "KODI", "SR22", "SR20", "P28B", "C550", "B36T", "DHC3", "DHC2", "GLEX", "B60T", "PC7", "E50P", "DA40", "AS50", "PA24", "C152", "ULAC", "BE30", "S550", "E300", "PA22", "J3", "B24", "B25", "B29", "B17", "PC6T", "T210", "BE36", "BE56", "P28R", "F406", "T51", "ST75", "CL60", "GL5T", "LJ24", "LJ25", "LJ31", "LJ40", "LJ55", "LJ75", "P38", "L10", "L12", "L29B", "L29A", "L14", "P2", "L37", "F2TH", "F900", "MYS4", "FA10", "DA50", "DJET", "PA25", "E200", "E230", "E400", "E500", "AS32", "AS3B", "AS55", "AS65", "EC45", "EC20", "EC30", "EC35", "EC55", "EC25", "TIGR", "BK17", "B412", "B06", "B205", "B212", "B222", "B230", "B407", "B427", "B430", "B47G", "A109", "A119", "A129", "B06T", "C421", "BE60", "TBM8", "PA31", "D401", "C500", "PA18", "R22", "R44", "C525", "PAY1", "PAY2", "PA30", "PRM1", "R66", "AEST", "EH10", "PA11", "BE18", "SIRA", "PA32", "M20P", "M20J", "C441", "B609", "LEG2", "BT36", "YK40", "TOBA", "BE55", "PZ04", "WT9", "L39", "C310", "PA20", "C56X", "E550", "CL35", "P180", "BE40", "YK18", "M20T", "PV1", "SH36", "P51", "T6", "SPIT", "C207", "PA28R", "A5", "PA34", "CHIN", "GL7T", "S92", "COL4", "PA46", "B462", "P46T", "LANC", "RV8", "G21", "AC68", "B429", "BN2P", "LJ35", "PA27", "TRIN", "UNIV", "AC90", "C402", "AN12", "HA4T", "MI8", "AN2", "GIV", "GLF4", "GLF2", "GLF6", "A210", "CAT", "CDC6", "PA38", "DO28", "GA5C", "B461", "B18T", "P28S", "C46", "EXPL", "B200", "DH2T", "AS21", "C68A", "PAY4", "B463", "PC24", "SLG2", "ASTO", "SP6", "SP7", "P166", "P66P", "P66T", "S360", "DC3T", "C77R", "E545", "FA5X", "G400", "S22T", "ECHO", "MJ5", "AC14", "C414", "MU2", "PA44", "SREY", "EFOX", "C185", "PAY3", "G115", "M200", "TB20", "P28T", "GLID", "P111", "SF25", "VW10", "P32R", "AP28", "DHC4", "A22", "PRPR", "D8", "DH3T", "BE99", "PA47", "AA5", "BDOG", "DV20", "A33");

# Try to put mil aircraft at mil spots
$milaircraft = array("F35", "T38", "F15", "F14", "F22", "F18", "A10", "F4", "C130", "B52", "B1", "B2", "CV22", "MV22", "V22", "H60", "CH47", "CH55", "C5", "C17", "C141", "EA6B", "A6", "P8", "P3", "P3C", "E3", "E3CF", "E3TF", "C97", "E6", "K35A", "K35E", "K35R", "KE3", "R135", "HAR", "E2", "C2", "B58", "EUFI", "SU11", "SU15", "SU17", "SU20", "SU22", "SU24", "SU25", "SU35", "SU30", "SU32", "SU34", "SU27", "MG29", "MG31", "E767", "U2", "SR71", "A4", "RQ1", "MQ9", "CH60", "H64", "H46", "H47", "H66", "F104", "F117", "VF35", "S3", "T33", "A7", "F8", "MIR2", "MIRA", "MIR4", "MRF1", "RFAL", "ETAR", "SMB2", "AJET", "F106", "F101", "MG21", "A400", "F18H", "VULC", "SUCO", "A50", "H53", "V35B", "C30J", "MH60", "TEX2", "F35A", "CNBR", "T160", "V10", "TOR", "AN22", "F5", "UH1Y", "AN32", "CN35", "AN26");

// MAKE THIS SELECTABLE
$actoadd = 3;

$theseacs = array();

for ($i=0; $i < $actoadd; $i++) {
  $newfp = $flightplans[$i];
  $nextfp = manglefp($newfp);
  $nextspot = usespot($newfp, $parkingspots);
  if ($nextspot != "") {
    if (in_array($usedspots, $nextspot)) {
      foreach (array($cargospots, $gaspots, $milspots, $otherspots) as &$thislist) {
        if (in_array($nextspot,$thislist)) {
          // set thislist and nextspot
        }
      }
    } else {
      foreach (array($cargospots, $gaspots, $milspots, $otherspots) as &$thislist) {
        if (in_array($nextspot,$thislist)) {
          //move nextspot to end of thislist
        }
      }
    }
  } else {
    // Using random spot
    $airline = substr($newfp['callsign'],0,2);
    $aircraft = splittype($newfp['planned_aircraft'])[1];
    if ( (in_array($airline, $cargoairlines)) && ($cargospots != array()) ) {
      //place in cargo
    } elseif ( (in_array($aircraft, $gaaircraft)) && ($gaspots != array())) {
      //place in GA
    } elseif ( (in_array($aircraft, $milaircraft)) && ($milspots != array())) {
      //place in mil
    } else {
      //place at term
    }
  }
  $usedspots[] = $nextspot;
  $theseacs[] = array($nextfp, $nextspot);
  // Could write table here
}
$outfile = "";
makeairfile($theseacs, $fieldelev, $outfile);

?>

<h2>Flight Plans from <?php echo $icao ?></h2>
<!--<div class="tooltip" style="margin-top:100px;">Hover over me
  <span class="tooltiptext">WAFDOF</span>
</div>-->
<?php
$total = count($fps);
$calls = count($flightplans);
echo "<p>Found ".$total." flight plans and ".$calls." unique callsigns</p>";
//array($csign, $actype, $dest, $alt, $rules, $rmks, $route);
?>
<div class="flighttable">
<table><tr><th>Callsign</th><th>Type</th><th>Rules</th><th>Spot</th><th>Dest</th><th>Alt</th><th>Route</th></tr>
<?php
$origincoords = aptcoords($icao);
foreach ($theseacs as $thisac) {
  echo "<p>".var_dump($thisac[0][1][3])."</p>";
  //mangles: type, alt, dest, route, rules
  echo "<tr><td>".$thisac[0][0]['callsign']."</td>";
  if ($thisac[0][1][0] != "") {
    $ac_cell = "<td class='tdm'><div class='tooltip'>".$thisac[0][0]['planned_aircraft']."<span class='tooltiptext'>".$thisac[0][1][0]."</span>";
  } else {
    $ac_cell = "<td>".$thisac[0][0]['planned_aircraft'];
  }
  echo $ac_cell."</td>";
  if ($thisac[0][1][4] != "") {
    $rules_cell = "<td class='tdm'><div class='tooltip'>".$thisac[0][0]['planned_flighttype']."<span class='tooltiptext'>".$thisac[0][1][4]."</span>";
  } else {
    $rules_cell = "<td>".$thisac[0][0]['planned_flighttype'];
  }
  echo $rules_cell."</td>";
  echo "<td>".$thisac[1][0]."</td>";
  if ($thisac[0][1][2] != "") {
    $dest_cell = "<td class='tdm'><div class='tooltip'>".$thisac[0][0]['planned_destairport']."<span class='tooltiptext'>".$thisac[0][1][2]."</span>";
    $destcoords = aptcoords($thisac[0][1][2]);
  } else {
    $dest_cell = "<td>".$thisac[0][0]['planned_destairport'];
    $destcoords = aptcoords($thisac[0][0]['planned_destairport']);
  }
  echo $dest_cell."</td>";

  $dof = inithdg($origincoords, $destcoords) - $magvar;
  $alt = $thisac[0][0]['planned_altitude'];
  if (($dof < 180 ) || ($dof == 360)) {
    if ( ($alt/1000)%2 != 1 ) {
      if ($thisac[0][1][1] != "") {
        $alt_cell = "<td class='tdm'><div class='tooltip'>".$alt."<span class='tooltiptext'>".$thisac[0][1][1]."</span>";
      } else {
        $alt_cell = "<td class='tdv'><div class='tooltip'>".$alt."<span class='tooltiptext'>WAFDOF</span>";
      }
    } else {
      $alt_cell = "<td>".$alt;
    }
  } else {
    if ( ($alt/1000)%2 != 0 ) {
      if ($thisac[0][1][1] != "") {
        $alt_cell = "<td class='tdm'><div class='tooltip'>".$alt."<span class='tooltiptext'>".$thisac[0][1][1]."</span>";
      } else {
        $alt_cell = "<td class='tdv'><div class='tooltip'>".$alt."<span class='tooltiptext'>WAFDOF</span>";
      }
    } else {
      $alt_cell = "<td>".$alt;
    }
  }
  echo $alt_cell."</td>";

  if ($thisac[0][1][3] != "") {
    //$mangled((0 nuke, >0 elems), origroute)
    $route_cell = "<td class='tdm'><div class='tooltip'>".$thisac[0][0]['planned_route']."<span class='tooltiptext'>".$thisac[0][1][3][1]."</span>";
  } else {
    $route_cell = "<td>".$thisac[0][0]['planned_route'];
  }
  echo $route_cell."</td></tr>\n";
}
 ?>
</table>
<form action=""><p>Get <input type="text" name="actoget" style="width:20px;"> more aircraft. <input type="submit" value="submit"></p>
</div>
</body>
</html>
