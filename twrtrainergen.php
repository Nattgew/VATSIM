<?php

ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

include_once 'logdbconfig.php';
include_once 'locdbconfig.php';
//TODO: Database with aircraft engine types
//include_once 'etype.php';
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
  border-bottom: 1px dotted black; /* If you want dots under the hoverable text */
}

.tooltip.warn {
  background: #f99;
}

.tooltip.caut {
  background: #fc6;
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
  $myfile = fopen($outfile, "w");
  foreach ($acs as $ac) {
    $fpline = fptoline($ac[0], $felev)."\n";
    //fwrite($myfile,$fpline);
  }
  fclose($myfile);
  // Process download
  if(file_exists($outfile)) {
    header('Content-Description: File Transfer');
    header('Content-Type: application/octet-stream');
    header('Content-Disposition: attachment; filename="'.basename($outfile).'"');
    header('Expires: 0');
    header('Cache-Control: must-revalidate');
    header('Pragma: public');
    header('Content-Length: ' . filesize($outfile));
    flush(); // Flush system output buffer
    readfile($outfile);
    //exit;
  }
}

function fptoline(array $ac, int $felev) {
  # Callsign:Type:Engine:Rules:Dep Field:Arr Field:Crz Alt:Route:Remarks:Sqk Code:Sqk Mode:Lat:Lon:Alt:Speed:Heading
  # ac[0] = fp
  # ac[1] = spot
  #echo "<p>".var_dump($ac)."</p>";
  $type = splittype($ac[0]['planned_aircraft'])[1];
  // External function will take care of exceptions
  engine = etype(strtoupper(type)));
  # TODO: find a better way to do this
  # Add main elements from flight plan
  $lit = array($ac[0]['callsign'], $ac[0]['planned_aircraft'], engine, $ac[0]['planned_flighttype'], $ac[0]['planned_depairport'], $ac[0]['planned_destairport'], $ac[0]['planned_altitude'], $ac[0]['planned_route'], $ac[0]['planned_remarks']);
  # Read transponder, set random mode if needed
  $xpdr = $ac[0]['transponder'];
  if ($xpdr == "0") {
    $xpdr = $getrndsq();
  }
  $lit[] = $xpdr;
  // Just get random mode
  $lit[] = $getrndmode();
  # Coordinates of parking spot
  $lit[] = (string) $ac[1][1][0];
  $lit[] = (string) $ac[1][1][1];
  # Field elevation
  $lit[] = $felev;
  # Speed and heading
  $lit[] = "0";
  # Ideally we'd verify the data is at the gate but this is at least as good as 360, right?
  $lit[] = $ac[0]['heading'];
  # print(lit)
  # Print out a string for each flight plan's main details
  #string = "%s | %s %s | %s -> %s | %s | %s" % ($ac[0]['callsign'], $ac[0]['planned_aircraft'], $ac[1][0], $ac[0]['planned_depairport'], $ac[0]['planned_destairport'], $ac[0]['planned_altitude'], $ac[0]['planned_route'])
  #print(string)
  # Automatically copy to clipboard
  #addtoclipboard(string)
  return implode(":",$lit);
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
      $hdg = $row["heading"];
      $fps[] = array("callsign" => $csign, "planned_aircraft" => $actype,
                     "planned_destairport" => $dest, "planned_altitude" => $alt,
                     "planned_flighttype" => $rules, "planned_remarks" => $rmks,
                     "planned_route" => $route, "time_logon" => $logon,
                     "planned_depairport" => $apt, "heading" => $hdg);
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
    // Just keep the random route
  } elseif (rand(0,100) < $chance_dct*100) {
    $newroute = "DCT";
  } elseif (rand(0,100) < $chance_blk*100) {
    $newroute = "";
  } else {
    $origpoints = multiexplode(array(" ","|","."),$route);
    $newpoints = multiexplode(array(" ","|","."), $newroute);
    $elemstoswap = rand(1,4);
    $mangledpoints = array_merge( array_slice($newpoints, 0, $elemstoswap), array_slice($origpoints, $elemstoswap) );
    $newroute = implode(" ", $mangledpoints);
    $mangletype = array($elemstoswap, array_slice($origpoints, 0, $elemstoswap));
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
  $ec = $typefields[2];
  $newwt = $wt;
  $mangled = array("", "", "");
  if ($wt != "") {
    # Already has a prefix
    if (rand(0,1) == 1) {
      # Mess with it
      $mangled[0] = $wt;
      if ($wt == "T") {
        # Switch T to H, hilarious!
        $newwt = "H/";
        # There's no option to leave it off because that's too easy, they don't need it anyway
      } elseif ($wt == "H") {
        # Switch H to something else!
        if (rand(0,1) == 1) {
          $newwt = "";
        } else {
          $newwt = "T/";
        }
      }
    } else {
      # Leave existing, just add /
      $newwt = $wt . "/";
    }
  } else {
    # No prefix existing
    if (rand(0,1) == 1) {
      # Mess with it
      $mangled[0] = 1; # 1 indicates it was blank and we added something
      if (rand(0,1) == 1) {
        $newwt = "T/";
      } else {
        $newwt = "H/";
      }
    }
  }
  # Mess with equipment code
  if ($ec == "") {
    $mangled[2] = 1; # 1 indicates it was blank and we added something
  } else {
    $mangled[2] = $ec;
  }
  $newec = rndeqpcode();
  # Put back together again
  $newtype = $newwt . $typefields[1] . $newec;
  return array($newtype, $mangled);
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
  // TODO: ADD WAY TO ADJUST THESE
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
    // $mangled[0] = $fp['planned_aircraft'];
    $mreturn = mangleec($fp['planned_aircraft']);
    $fp['planned_aircraft'] = $mreturn[0];
    $mangled[0] = $mreturn[1];
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
  foreach ($coords as $loc) {
    $dists = array();
    foreach ($spots as $spot) {
      $dists[] = array($spot, cosinedist($loc, $spot[1]));
    }
    usort($dists, 'cmp');
    echo "<p>Closest: ".dists[0][1]." Furthest: ".dists[-1][1]."</p>";
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

function loopiter(array $theiter) {
  # Move first item to end of list, return new list
  # Python also returned first item but that seems less convenient in PHP
  $nextspot = $theiter[0];
  array_splice($theiter,0,1);
  $theiter[] = $nextspot;
  return $theiter;
}

// Read apt file to get parking spots
// Full list used for matching original spots
$parkingspots = array();

// Special lists used for giving random spots
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

//echo "<p>Found ".count($parkingspots)." parking spots";

// Get lists of parking spots
foreach ($parkingspots as $spot) {
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

# TODO: Consider only grabbing the earliest FP revision
#       This is closest to what the pilots filed, which is what we're after
#       Then you don't have to worry about searching for the coordinates at the gate
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

# The following lists are only used to determine a spot if the logged location does not match a gate
# Airlines to put on cargo ramps
$cargoairlines = array("FDX", "UPS", "GEC", "GTI", "ATI", "DHL", "BOX", "CLX", "ABW", "SQC", "ABX", "AEG", "AJT", "CLU", "BDA", "DAE", "DHK", "JOS", "RTM", "DHX", "BCS", "CKS", "MPH", "NCA", "PAC", "TAY", "RCF", "CAO", "TPA", "CKK", "MSX", "LCO", "SHQ", "LTG", "ADB");

# Aircraft to put on GA ramp
# For aircraft not listed, would rather have GA at term than airliner at GA
$gaaircraft = array("C172", "C182", "PC12", "C208", "PA28", "BE35", "B350", "FA20", "C750", "CL30", "C25", "BE58", "BE9L", "HAWK", "C150", "P06T", "H25B", "TBM7", "P28U", "BE33", "AC11", "DHC6", "EA50", "SF50", "C510", "M7", "DC3", "UH1", "E55P", "TBM9", "PC21", "C25A", "B58T", "H850", "BE20", "DA42", "S76", "Z50", "A139", "C206", "AC50", "EPIC", "LJ45", "LJ60", "C404", "FA50", "C170", "GLF5", "C210", "FA7X", "DA62", "DR40", "P28A", "KODI", "SR22", "SR20", "P28B", "C550", "B36T", "DHC3", "DHC2", "GLEX", "B60T", "PC7", "E50P", "DA40", "AS50", "PA24", "C152", "ULAC", "BE30", "S550", "E300", "PA22", "J3", "B24", "B25", "B29", "B17", "PC6T", "T210", "BE36", "BE56", "P28R", "F406", "T51", "ST75", "CL60", "GL5T", "LJ24", "LJ25", "LJ31", "LJ40", "LJ55", "LJ75", "P38", "L10", "L12", "L29B", "L29A", "L14", "P2", "L37", "F2TH", "F900", "MYS4", "FA10", "DA50", "DJET", "PA25", "E200", "E230", "E400", "E500", "AS32", "AS3B", "AS55", "AS65", "EC45", "EC20", "EC30", "EC35", "EC55", "EC25", "TIGR", "BK17", "B412", "B06", "B205", "B212", "B222", "B230", "B407", "B427", "B430", "B47G", "A109", "A119", "A129", "B06T", "C421", "BE60", "TBM8", "PA31", "D401", "C500", "PA18", "R22", "R44", "C525", "PAY1", "PAY2", "PA30", "PRM1", "R66", "AEST", "EH10", "PA11", "BE18", "SIRA", "PA32", "M20P", "M20J", "C441", "B609", "LEG2", "BT36", "YK40", "TOBA", "BE55", "PZ04", "WT9", "L39", "C310", "PA20", "C56X", "E550", "CL35", "P180", "BE40", "YK18", "M20T", "PV1", "SH36", "P51", "T6", "SPIT", "C207", "PA28R", "A5", "PA34", "CHIN", "GL7T", "S92", "COL4", "PA46", "B462", "P46T", "LANC", "RV8", "G21", "AC68", "B429", "BN2P", "LJ35", "PA27", "TRIN", "UNIV", "AC90", "C402", "AN12", "HA4T", "MI8", "AN2", "GIV", "GLF4", "GLF2", "GLF6", "A210", "CAT", "CDC6", "PA38", "DO28", "GA5C", "B461", "B18T", "P28S", "C46", "EXPL", "B200", "DH2T", "AS21", "C68A", "PAY4", "B463", "PC24", "SLG2", "ASTO", "SP6", "SP7", "P166", "P66P", "P66T", "S360", "DC3T", "C77R", "E545", "FA5X", "G400", "S22T", "ECHO", "MJ5", "AC14", "C414", "MU2", "PA44", "SREY", "EFOX", "C185", "PAY3", "G115", "M200", "TB20", "P28T", "GLID", "P111", "SF25", "VW10", "P32R", "AP28", "DHC4", "A22", "PRPR", "D8", "DH3T", "BE99", "PA47", "AA5", "BDOG", "DV20", "A33");

# Try to put mil aircraft at mil spots
$milaircraft = array("F35", "T38", "F15", "F14", "F22", "F18", "A10", "F4", "C130", "B52", "B1", "B2", "CV22", "MV22", "V22", "H60", "CH47", "CH55", "C5", "C17", "C141", "EA6B", "A6", "P8", "P3", "P3C", "E3", "E3CF", "E3TF", "C97", "E6", "K35A", "K35E", "K35R", "KE3", "R135", "HAR", "E2", "C2", "B58", "EUFI", "SU11", "SU15", "SU17", "SU20", "SU22", "SU24", "SU25", "SU35", "SU30", "SU32", "SU34", "SU27", "MG29", "MG31", "E767", "U2", "SR71", "A4", "RQ1", "MQ9", "CH60", "H64", "H46", "H47", "H66", "F104", "F117", "VF35", "S3", "T33", "A7", "F8", "MIR2", "MIRA", "MIR4", "MRF1", "RFAL", "ETAR", "SMB2", "AJET", "F106", "F101", "MG21", "A400", "F18H", "VULC", "SUCO", "A50", "H53", "V35B", "C30J", "MH60", "TEX2", "F35A", "CNBR", "T160", "V10", "TOR", "AN22", "F5", "UH1Y", "AN32", "CN35", "AN26");

# For checking if it needs an S/H
$supers = array("A225", "A380", "H4", "SLCH");
$heavies = array("B748", "B744", "B743", "B742", "B741", "B747", "A124", "C5", "A346", "A345", "A343", "A342", "A340", "B773", "B772", "B77F", "B77L", "B77W", "A359", "A35K", "A350", "MD11", "DC10", "MD10", "IL96", "IL86", "B788", "B789", "B78X", "B787", "L101", "B764", "B763", "B762", "B767", "E767", "KC46", "CONC", "A30B", "A306", "A3ST", "A300", "A310", "VC10", "B703", "B707", "DC86", "DC83", "A400");

// MAKE THIS SELECTABLE
$actoadd = 3;

$theseacs = array();

for ($i=0; $i < $actoadd; $i++) {
  // Keep list of recently used spots to limited set
  if (count($usedspots) > 14) {
    // Remove first item in list (new ones are appended to bottom)
    array_splice($usedspots, 0, 1);
  }
  // TODO: splice this or whatever we need to do
  $newfp = $flightplans[$i];
  $nextfp = manglefp($newfp);
  $nextspot = usespot($newfp, $parkingspots);
  if ($nextspot != "") {
    if (in_array($usedspots, $nextspot)) {
      // Too recent, pick next spot in the same list
      foreach (array($cargospots, $gaspots, $milspots, $otherspots) as &$thislist) {
        if (in_array($nextspot,$thislist)) {
          // Use next spot in this list
          $nextspot = $thislist[0];
          // Send this spot to bottom of list
          $thislist = loopiter($thislist);
        }
      }
    } else {
      // Not too recent, just move to bottom of list
      foreach (array($cargospots, $gaspots, $milspots, $otherspots) as &$thislist) {
        if (in_array($nextspot,$thislist)) {
          // move nextspot to end of thislist
          array_splice($thislist,array_search($nextspot,$thislist),1);
          $thislist[] = $nextspot;
        }
      }
    }
  } else {
    // Using random spot
    $airline = substr($newfp['callsign'],0,2);
    $aircraft = splittype($newfp['planned_aircraft'])[1];
    if ( (in_array($airline, $cargoairlines)) && ($cargospots != array()) ) {
      $nextspot = $cargospots[0];
      $cargospots = loopiter($cargospots);
    } elseif ( (in_array($aircraft, $gaaircraft)) && ($gaspots != array())) {
      $nextspot = $gaspots[0];
      $gaspots = loopiter($gaspots);
    } elseif ( (in_array($aircraft, $milaircraft)) && ($milspots != array())) {
      $nextspot = $milspots[0];
      $milspots = loopiter($milspots);
    } else {
      $nextspot = $otherspots[0];
      $otherspots = loopiter($milspots);
    }
  }
  // Add this spot to bottom of the recently used spots list
  $usedspots[] = $nextspot;
  // Add this one to the list of current aircraft
  $theseacs[] = array($nextfp, $nextspot);
  // Could write table here
}
// Path to output file
$outfile = "";
makeairfile($theseacs, $fieldelev, $outfile);

?>

<h2>Flight Plans from <?php echo $icao ?></h2>

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
  #echo "<p>".var_dump($thisac[0][1][3])."</p>";
  # Callsign not touched
  echo "<tr><td>".$thisac[0][0]['callsign']."</td>";
  //mangles: type, alt, dest, route, rules
  $typefields = splittype($thisac[0][0]['planned_aircraft']);
  if ($thisac[0][1][0] != "") {
    # Process the mangled type field
    
    $wt = $typefields[0];
    if ($wt != "") {
      $wt = $wt . "/";
    } else {
      $wt = "&nbsp;&nbsp;";
    }
    if ($thisac[0][1][0][0] == 1) {
      # No previous pre, added one
      $ttw = "Added";
    } else {
      # Changed existing pre
      $ttw = $thisac[0][1][0][0];
    }
    $wtc = "<div class='tooltip warn'>".$wt."<span class='tooltiptext'>".$ttw."</span></div>";
    
    $ec = $typefields[2];
    if ($ec != "") {
      $ec = "/" . $ec;
    } else {
      $ec = "&nbsp;&nbsp;";
    }
    if ($thisac[0][1][0][2] == 1) {
      # No previous ec, added one
      $tte = "Added";
    } else {
      # Changed existing ec
      $tte = $thisac[0][1][0][2];
    }
    $ecc = "<div class='tooltip warn'>".$ec."<span class='tooltiptext'>".$tte."</span></div>";
    
    $ac_cell = "<td>".$wtc.$typefields[1].$ecc;
  } else {
    # No tampering but we'll check it
    # TODO: Make weight check a function
    if (in_array($typefields[1]), $heavies) {
      if ( $typefields[0] != "H" ) {
        $ttw = "Heavy";
        if ($typefields[0] == "") {
          $wt = "&nbsp;&nbsp;";
        } else {
          $wt = $typefields[0] . "/";
        }
        $wtc = "<div class='tooltip caut'>".$wt."<span class='tooltiptext'>".$ttw."</span></div>";
      }
    } elseif (in_array($typefields[1]), $supers) {
      if ( $typefields[0] != "S" ) {
        $ttw = "Super";
        if ($typefields[0] == "") {
          $wt = "&nbsp;&nbsp;";
        } else {
          $wt = $typefields[0] . "/";
        }
        $wtc = "<div class='tooltip caut'>".$wt."<span class='tooltiptext'>".$ttw."</span></div>";
      }
    } elseif ($typefields[0] != "") {
      if ( $typefields[0] == "T" ) {
        # UNNECESSARY!
        $wt = $typefields[0]."/";
        $ttw = "Remove";
      } else {
        # Wrong!
        $wt = $typefields[0]."/";
        $ttw = "Wrong";
      }
      $wtc = "<div class='tooltip caut'>".$wt."<span class='tooltiptext'>".$ttw."</span></div>";
      
    } else {
      // All good for weight
      $wtc = "";
    }
    
    $ec = "/".$typefields[2];
    $commonec = array("L", "A", "G");
    if (!in_array($typefields[2], $commonec) {
      $ecc = "<div class='tooltip caut'>".$ec."<span class='tooltiptext'>Strange</span></div>";
    } else {
      # TODO: Could get more involved here
      $ecc = $ec;
    }
    
    $ac_cell = "<td>".$wtc.$typefields[1].$ecc;
  }
  echo $ac_cell."</td>";
  if ($thisac[0][1][4] != "") {
    $rules_cell = "<td class='tdm'><div class='tooltip'>".$thisac[0][0]['planned_flighttype']."<span class='tooltiptext'>".$thisac[0][1][4]."</span></div>";
  } else {
    $rules_cell = "<td>".$thisac[0][0]['planned_flighttype'];
  }
  echo $rules_cell."</td>";
  echo "<td>".$thisac[1][0]."</td>";
  if ($thisac[0][1][2] != "") {
    $dest_cell = "<td class='tdm'><div class='tooltip'>".$thisac[0][0]['planned_destairport']."<span class='tooltiptext'>".$thisac[0][1][2]."</span></div>";
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
        $alt_cell = "<td class='tdm'><div class='tooltip'>".$alt."<span class='tooltiptext'>".$thisac[0][1][1]."</span></div>";
      } else {
        $alt_cell = "<td class='tdv'><div class='tooltip'>".$alt."<span class='tooltiptext'>WAFDOF</span></div>";
      }
    } else {
      $alt_cell = "<td>".$alt;
    }
  } else {
    if ( ($alt/1000)%2 != 0 ) {
      if ($thisac[0][1][1] != "") {
        $alt_cell = "<td class='tdm'><div class='tooltip'>".$alt."<span class='tooltiptext'>".$thisac[0][1][1]."</span></div>";
      } else {
        $alt_cell = "<td class='tdv'><div class='tooltip'>".$alt."<span class='tooltiptext'>WAFDOF</span></div>";
      }
    } else {
      $alt_cell = "<td>".$alt;
    }
  }
  echo $alt_cell."</td>";

  if ($thisac[0][1][3] != "") {
    //$mangled((0 nuke, >0 elems), origroute)
    if ($thisac[0][1][3][0] == 0) {
      $mangledpart = $thisac[0][0]['planned_route'];
      $therest = "";
    } else {
      $routeelems = multiexplode(array(" ","|","."),$thisac[0][0]['planned_route']);
      $mangledpart = implode(" ", array_slice($routeelems, 0, $thisac[0][1][3][0]));
      $therest = implode(" ", array_slice($routeelems, $thisac[0][1][3][0]));
    }
    $route_cell = "<td><div class='tooltip'>".$mangledpart."<span class='tooltiptext'>".$thisac[0][1][3][1]."</span></div>".$therest;
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
