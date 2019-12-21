<?php

ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

include_once 'logdbconfig.php';
include_once 'locdbconfig.php';
include_once 'engtype.php';
?>
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>TWRTrainer Generator</title>
<meta name="description" content="TWRTrainer Generator">
<meta name="author" content="N">
<link rel="stylesheet" href="style.css">
<link rel="stylesheet" href="twrtrainerstyle.css">
<style>
</style>
</head>
<body>

<?php
# Read posted vars
if( $_POST["icao"] ) {
  $icao = $_POST['icao'];
} else {
  $icao = "Invalid ICAO";
}

if( $_POST["actoadd"] ) {
  $actoadd = $_POST['actoadd'];
} else {
  $actoadd = 5;
}

# Work out the error rates
$error_rates = array();
if( $_POST["chance_ec"] ) {
  $error_rates['ec'] = $_POST['chance_ec'];
} else {
  $error_rates['ec'] = 0.5;
}
if( $_POST["chance_alt"] ) {
  $error_rates['alt'] = $_POST['chance_alt'];
} else {
  $error_rates['alt'] = 0.25;
}
if( $_POST["chance_dest"] ) {
  $error_rates['dest'] = $_POST['chance_dest'];
} else {
  $error_rates['dest'] = 0.01;
}
if( $_POST["chance_route"] ) {
  $error_rates['route'] = $_POST['chance_route'];
} else {
  $error_rates['route'] = 0.25;
}
if( $_POST["chance_rules"] ) {
  $error_rates['rules'] = $_POST['chance_rules'];
} else {
  $error_rates['rules'] = 0.1;
}
$error_rates['route_opt'] = array();
if( $_POST["chance_route_swap"] ) {
  $error_rates['route_opt']['swap'] = $_POST['chance_route_swap'];
} else {
  $error_rates['route_opt']['swap'] = 0.1;
}
if( $_POST["chance_route_dct"] ) {
  $error_rates['route_opt']['dct'] = $_POST['chance_route_dct'];
} else {
  $error_rates['route_opt']['dct'] = 0.05;
}
if( $_POST["chance_route_blk"] ) {
  $error_rates['route_opt']['blk'] = $_POST['chance_route_blk'];
} else {
  $error_rates['route_opt']['blk'] = 0.05;
}


# TODO: Split (most) functions out
# https://www.php.net/manual/en/function.array-unique.php#116302
function unique_multidim_array($array, $key) {
  $temp_array = array();
  $i = 0;
  $key_array = array();
  #echo "\nMultidim length: ".count($array)."\n";
  foreach($array as $val) {
    # echo $i;
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

# https://www.php.net/manual/en/function.explode.php#111307
function multiexplode ($delimiters,$string) {
  $ready = str_replace($delimiters, $delimiters[0], $string);
  $launch = explode($delimiters[0], $ready);
  return  $launch;
}

# Used with usort to sort based on key
function cmp(array $a, array $b) {
  if ($a[1] < $b[1]) {
    return -1;
  } else if ($a[1] > $b[1]) {
    return 1;
  } else {
    return 0;
  }
}

function makeairfile(array $acs, int $felev, string $outfile) {
  $myfile = fopen($outfile, "w");
  foreach ($acs as $ac) {
    $fpline = fptoline($ac, $felev)."\n";
    fwrite($myfile,$fpline);
  }
  fclose($myfile);
  # Process download
  # dlfile($outfile);
}

function dlfile(string $outfile) {
  if(file_exists($outfile)) {
    header('Content-Description: File Transfer');
    header('Content-Type: application/octet-stream');
    header('Content-Disposition: attachment; filename="'.basename($outfile).'"');
    header('Expires: 0');
    header('Cache-Control: must-revalidate');
    header('Pragma: public');
    header('Content-Length: ' . filesize($outfile));
    flush(); # Flush system output buffer
    readfile($outfile);
    # exit;
  }
}

# Returns a random squawk code
function getrndsq() {
  $sq = "";
  while (in_array($sq, array("", "7500", "7600", "7700"))) {
    for ($i=0; $i<4; $i++) {
      $sq .= (string) rand(0,7);
    }
  }
  return $sq;
}

# Returns random normal/standby mode
function getrndmode() {
  if (rand(0,1) == 1) {
    $mode = "N";
  } else {
    $mode = "S";
  }
  return $mode;
}

# Convert a flight plan in $ac to a line in the .air file
function fptoline(array $ac, int $felev) {
  # Callsign:Type:Engine:Rules:Dep Field:Arr Field:Crz Alt:Route:Remarks:Sqk Code:Sqk Mode:Lat:Lon:Alt:Speed:Heading
  # ac[0] = fp
  # ac[1] = spot
  #echo "<p>".var_dump($ac)."</p>";
  $type = splittype($ac[0][0]['planned_aircraft'])[1];
  # External function will take care of exceptions
  $engine = etype(strtoupper($type));
  # TODO: find a better way to do this
  # Add main elements from flight plan
  $lit = array($ac[0][0]['callsign'], $ac[0][0]['planned_aircraft'], $engine, $ac[0][0]['planned_flighttype'], $ac[0][0]['planned_depairport'], $ac[0][0]['planned_destairport'], $ac[0][0]['planned_altitude'], $ac[0][0]['planned_route'], $ac[0][0]['planned_remarks']);
  # Read transponder, set random mode if needed
  $xpdr = $ac[0][0]['transponder'];
  if ($xpdr == "0") {
    $xpdr = getrndsq();
  }
  $lit[] = $xpdr;
  # Just get random mode
  $lit[] = getrndmode();
  # Coordinates of parking spot
  #echo "<p>".var_dump($ac)."</p>";
  $lit[] = (string) $ac[1][1][0];
  $lit[] = (string) $ac[1][1][1];
  # Field elevation
  $lit[] = $felev;
  # Speed and heading
  $lit[] = "0";
  # Ideally we'd verify the data is at the gate but this is at least as good as 360, right?
  $lit[] = $ac[0][0]['heading'];
  # print(lit)
  # Print out a string for each flight plan's main details
  #string = "%s | %s %s | %s -> %s | %s | %s" % ($ac[0]['callsign'], $ac[0]['planned_aircraft'], $ac[1][0], $ac[0]['planned_depairport'], $ac[0]['planned_destairport'], $ac[0]['planned_altitude'], $ac[0]['planned_route'])
  #print(string)
  # Automatically copy to clipboard
  #addtoclipboard(string)
  return implode(":",$lit);
}

# Returns all flight plans departing from $icao
function getfplist(string $icao) {
  global $conn;
  $sql = "SELECT * FROM `flights` WHERE planned_depairport = ?";
  $stmt = $conn->prepare($sql);
  $stmt->bind_param("s", $icao);
  $stmt->execute();
  $result = $stmt->get_result();

  $fps = array();

  #keys = ["callsign", "cid", "realname", "clienttype", "frequency", "latitude", "longitude", "altitude", "groundspeed", "planned_aircraft", "planned_tascruise", "planned_depairport", "planned_altitude", "planned_destairport", "server", "protrevision", "rating", "transponder", "facilitytype", "visualrange", "planned_revision", "planned_flighttype", "planned_deptime", "planned_actdeptime", "planned_hrsenroute", "planned_minenroute", "planned_hrsfuel", "planned_minfuel", "planned_altairport", "planned_remarks", "planned_route", "planned_depairport_lat", "planned_depairport_lon", "planned_destairport_lat", "planned_destairport_lon", "atis_message", "time_last_atis_received", "time_logon", "heading", "QNH_iHg", "QNH_Mb"]

  if ($result->num_rows > 0) {
    # output data of each row
    while($row = $result->fetch_assoc()) {
      # Could store them all but cherry pick for now
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
      $xpdr = $row["transponder"];
      $fps[] = array("callsign" => $csign, "planned_aircraft" => $actype,
                     "planned_destairport" => $dest, "planned_altitude" => $alt,
                     "planned_flighttype" => $rules, "planned_remarks" => $rmks,
                     "planned_route" => $route, "time_logon" => $logon,
                     "planned_depairport" => $apt, "heading" => $hdg,
                     "transponder" => $xpdr);
    }
  } else {
    echo "Could not find any flight plans!";
  }
  return $fps;
}

# Gets a random flight plan at $airport
function randomfp(string $airport) {
  $fplist = getfplist($airport);
  return $fplist[array_rand($fplist)];
}

# Converts the altitude string from FP to a number
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
      #echo "Number like acceptable person\n";
    } catch (Exception $e) {
      #echo "Could not determine altitude: ".$altstr."\n";
      $alt = (int) 0;
    }
  }
  #echo "ALT: ".$altstr." -> ".strval($alt)."<br/>";
  return $alt;
}

# Converts number to FL string
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

# Add or subtract 1000 feet to be wrong for direction
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

# Messes with the route
function mangleroute(string $airport, string $route, array $route_opt) {
  # Records the changes made
  # 0 means a swap/wipe of whole route
  $mangletype = array(0, $route);
  # Get a random route for lulz
  $newplan = randomfp($airport);
  $newroute = $newplan['planned_route'];
  if (rand(0,100) < $route_opt['swap']*100) {
    # Just keep the random route
  } elseif (rand(0,100) < $route_opt['dct']*100) {
    $newroute = "DCT";
  } elseif (rand(0,100) < $route_opt['blk']*100) {
    $newroute = "";
  } else {
    # Swap some of the beginning of the route
    $origpoints = multiexplode(array(" ","|","."),$route);
    $newpoints = multiexplode(array(" ","|","."), $newroute);
    $elemstoswap = rand(1,4);
    $mangledpoints = array_merge( array_slice($newpoints, 0, $elemstoswap), array_slice($origpoints, $elemstoswap) );
    $newroute = implode(" ", $mangledpoints);
    # Record number of elements changed, and the original elements
    $mangletype = array($elemstoswap, implode(" ",array_slice($origpoints, 0, $elemstoswap)));
  }
  return array($newroute, $mangletype);
}

# Shuffles all but first letter of dest airport
function mangledest(string $dest) {
  $first = substr($dest, 0, 1);
  $last = str_shuffle(substr($dest, 1));
  $shuffled = $first . $last;
  return $shuffled;
}

# Chooses random equipment code
function rndeqpcode() {
  # Could go with any letter but we'll limit it to some valid ones
  $validcodes = array('H', 'W', 'Z', 'L', 'X', 'T', 'U', 'D', 'B', 'A', 'M', 'N', 'P', 'Y', 'C', 'I', 'V', 'S', 'G');
  $thiscode = "/" . $validcodes[array_rand($validcodes)];
  #echo "<p>Chose random code: ".$thiscode."</p>";
  return $thiscode;
}

# Splits the aircraft type into weight, aircraft, and equipment code
function splittype(string $type) {
  # TODO: This could be more rigorous
  $fields = explode('/', $type);
  $wt = "";
  $ec = "";
  if (strlen($fields[0]) == 1) {
    # First field is single char
    if (count($fields) > 1) {
      # This must be the weight
      $wt = $fields[0];
      $type = $fields[1];
      if (count($fields) > 2) {
        # We have all three
        $ec = $fields[2];
      }
    } else {
      # Single letter? We'll roll with it
      $type = $fields[0];
    }
  } else {
    # Assume if it's multiple chars it's the type
    $type = $fields[0];
    if (count($fields) > 1) {
      # If there's another it must be the equipment code
      $ec = $fields[1];
    }
  }
  return array($wt, $type, $ec);
}

# Break the equipment code, very popular with students
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
      # Record original prefix
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
      } else {
        # Something wrong that we'll leave there
        $newwt = $wt;
        # Nothing changed
        $mangled[0] = "";
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
  # If it's blank, just leave it
  if ( $ec != "" ) {
    # Record original code
    $mangled[2] = $ec;
    if (rand(1,10)<2) {
      # Get a random one
      $newec = $ec;
      # Don't choose the same one we already have, silly
      while ($newec == $ec) {
        $newec = rndeqpcode();
      }
    } else {
      # More likely to just leave blank
      $newec = "";
    }
  } else {
    # Leave it blank
    $newec = "";
  }
  # Put back together again
  $newtype = $newwt . $typefields[1] . $newec;
  return array($newtype, $mangled);
}

# Swap flight rules, IFR/VFR
function manglerules(string $rules) {
  if ( $rules == "I" ) {
    $rules = "V";
  } else {
    $rules = "I";
  }
  # Small chance of seeing SVFR
  if (rand(0,100) < 2 ) {
    $rules = "S";
  }
  return $rules;
}

function manglefp(array $fp, array $error_rates) {
  # Could also store the mangles themselves here...

  # type, alt, dest, route, rules
  # Track all changes made
  $mangled = array_fill(0, 5, "");
  # Equipment code
  if (rand(0,100) < $error_rates['ec'] * 100) {
    $mreturn = mangleec($fp['planned_aircraft']);
    $fp['planned_aircraft'] = $mreturn[0]; # New code
    $mangled[0] = $mreturn[1]; # Data on what changed
  }
  # Altitude
  # Don't even try to mangle low altitudes
  if ((rand(0,100) < $error_rates['alt'] * 100 ) && (alt_to_int($fp['planned_altitude']) > 999)) {
    $mangled[1] = $fp['planned_altitude'];
    $fp['planned_altitude'] = manglealt($fp['planned_altitude']);
  }
  # Destination
  if (rand(0,100) < $error_rates['dest'] * 100) {
    $mangled[2] = $fp['planned_destairport'];
    $fp['planned_destairport'] = mangledest($fp['planned_destairport']);
  }
  # Route
  if (rand(0,100) < $error_rates['route'] * 100) {
    $mreturn = mangleroute($fp['planned_depairport'], $fp['planned_route'], $error_rates['route_opt']);
    $fp['planned_route'] = $mreturn[0]; # New route
    $mangled[3] = $mreturn[1]; # Data on what changed
  }
  # Flight type
  if (rand(0,100) < $error_rates['rules'] * 100) {
    $mangled[4] = $fp['planned_flighttype'];
    $fp['planned_flighttype'] = manglerules($fp['planned_flighttype']);
  }
  return array($fp, $mangled);
}

# Find all locations for this session with ground speed of 0
# Could do by user/callsign, or even just callsign...
function getlocations(array $fp) {
  global $conn;
  $coords = array();
  $sql = 'SELECT latitude, longitude FROM flights WHERE callsign = ? AND time_logon = ? AND groundspeed = "0"';
  # Debugging but also due diligence
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

# Find the right parking spot to use
# TODO: record reasoning for no spot placement
function usespot(array $fp, array $spots) {
  # Leave blank unless we find a match
  $spotmatch = "";
  # Get all locations for this session
  $coords = getlocations($fp);
  foreach ($coords as $loc) {
    # Find distances from this location to all spots
    $dists = array();
    foreach ($spots as $spot) {
      $dists[] = array($spot, cosinedist($loc, $spot[1]));
    }
    usort($dists, 'cmp');
    #echo "<p>Closest: ".$dists[0][1]." Furthest: ".end($dists)[1]."</p>";
    # Consider original spot if closer than 200 feet
    if ($dists[0][1] < 200/6076) {
      #echo "<p>Matching original spot ".$dists[0][0][0]."</p>";
      $spotmatch = $dists[0][0];
      break;
    } else {
      # Give distance to spot it feet or nautical miles
      if ($dists[0][1] < 0.5) {
        $dstr = (string) round($dists[0][1]*6076) . "ft";
      } else {
        $dstr = (string) round($dists[0][1]) . "nmi";
      }
      $spotstr = "Closest spot ".$dists[0][0][0]." was ".$dstr." away";
      #echo "<p>".$spotstr."</p>";
    }
  }
  return $spotmatch;
}

# Distance in nautical miles between two sets of coordinates
function cosinedist(array $latlon1, array $latlon2) {
  #echo "Dist from ".var_dump($latlon1)." to ".var_dump($latlon2)."</p>";
  $lat1 = $latlon1[0];
  $lon1 = $latlon1[1];
  $lat2 = $latlon2[0];
  $lon2 = $latlon2[1];
  $phi1 = deg2rad($lat1);
  $phi2 = deg2rad($lat2);
  $dellamb = deg2rad($lon2-$lon1);
  $R = 3440.06479; # Nmi
  $d = acos(sin($phi1)*sin($phi2) + cos($phi1)*cos($phi2) * cos($dellamb)) * $R;
  return $d;
}

# Find heading between coordinates
function inithdg($latlon1,$latlon2) {
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

# Return coordiates of airport
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

# Read apt file to get parking spots and other info

# Full list used for matching original spots
$parkingspots = array();

# Special lists used for giving random spots
# They will be like decks of cards, shuffled and then drawn from the top
$gaspots = array();
$cargospots = array();
$milspots = array();
$otherspots = array();

$myfile = fopen("twrtrainer/".$icao.".apt", "r") or die("Unable to open file!");

$name = "";
$magvar = 0;
$fieldelev = "0";
while(! feof($myfile)) {
  $line = trim(fgets($myfile));
  if ($name <> "") {
    $coords = explode(" ",$line);
    $parkingspots[] = array($name, $coords);
  }
  if (substr($line,0,9) == "[PARKING ") {
    $name = substr($line, 9, -1);
    #echo "<p>Cut ".$name." from ".$line."</p>";
  } else {
    $name = "";
    # Search for other info we need
    if (substr($line,0,19) == "magnetic variation=" ) {
      # echo "<p>".$line."</p>";
      # echo "<p>Found magvar:".substr($line,19)."</p>";
      $magvar = (int)substr($line,19);
      # echo "<p>Set magvar:".$magvar."</p>";
    } elseif (substr($line,0,16) == "field elevation=" ) {
      # echo "<p>".$line."</p>";
      # echo "<p>Found felev: ".substr($line,16)."</p>";
      $fieldelev = substr($line,16);
    }
  }
}

# echo "<p>".var_dump($parkingspots)."</p>";

fclose($myfile);

# echo "<p>Found ".count($parkingspots)." parking spots";

# Sort into types of spots based on names
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

# Shuffle the deck
shuffle($gaspots);
shuffle($cargospots);
shuffle($milspots);
shuffle($otherspots);

# TODO: Consider only grabbing the earliest FP revision
#       This is closest to what the pilots filed, which is what we're after
#       Then you don't have to worry about searching for the coordinates at the gate (maybe)
# Getting list of flight plans from this airport
$fps = getfplist($icao);
#echo "<p>Found ".count($fps)." flight plans.</p>";
shuffle($fps);

# foreach ($fps as $fp) {
#   foreach ($fp as $elem) {
#     echo strval($elem)."<br/>";
#   }
# }

# Pick first instance of each callsign
$flightplans = unique_multidim_array($fps, "callsign");

# Keep track of recently used spots
$usedspots = array();

# The following lists are only used to determine a spot if logged position won't work
# Airlines to put on cargo ramps
$cargoairlines = array("FDX", "UPS", "GEC", "GTI", "ATI", "DHL", "BOX", "CLX", "ABW", "SQC", "ABX", "AEG", "AJT", "CLU", "BDA", "DAE", "DHK", "JOS", "RTM", "DHX", "BCS", "CKS", "MPH", "NCA", "PAC", "TAY", "RCF", "CAO", "TPA", "CKK", "MSX", "LCO", "SHQ", "LTG", "ADB");

# Aircraft to put on GA ramp
# For aircraft not listed, would rather have GA at term than airliner at GA
$gaaircraft = array("C172", "C182", "PC12", "C208", "PA28", "BE35", "B350", "FA20", "C750", "CL30", "C25", "BE58", "BE9L", "HAWK", "C150", "P06T", "H25B", "TBM7", "P28U", "BE33", "AC11", "DHC6", "EA50", "SF50", "C510", "M7", "DC3", "UH1", "E55P", "TBM9", "PC21", "C25A", "B58T", "H850", "BE20", "DA42", "S76", "Z50", "A139", "C206", "AC50", "EPIC", "LJ45", "LJ60", "C404", "FA50", "C170", "GLF5", "C210", "FA7X", "DA62", "DR40", "P28A", "KODI", "SR22", "SR20", "P28B", "C550", "B36T", "DHC3", "DHC2", "GLEX", "B60T", "PC7", "E50P", "DA40", "AS50", "PA24", "C152", "ULAC", "BE30", "S550", "E300", "PA22", "J3", "B24", "B25", "B29", "B17", "PC6T", "T210", "BE36", "BE56", "P28R", "F406", "T51", "ST75", "CL60", "GL5T", "LJ24", "LJ25", "LJ31", "LJ40", "LJ55", "LJ75", "P38", "L10", "L12", "L29B", "L29A", "L14", "P2", "L37", "F2TH", "F900", "MYS4", "FA10", "DA50", "DJET", "PA25", "E200", "E230", "E400", "E500", "AS32", "AS3B", "AS55", "AS65", "EC45", "EC20", "EC30", "EC35", "EC55", "EC25", "TIGR", "BK17", "B412", "B06", "B205", "B212", "B222", "B230", "B407", "B427", "B430", "B47G", "A109", "A119", "A129", "B06T", "C421", "BE60", "TBM8", "PA31", "D401", "C500", "PA18", "R22", "R44", "C525", "PAY1", "PAY2", "PA30", "PRM1", "R66", "AEST", "EH10", "PA11", "BE18", "SIRA", "PA32", "M20P", "M20J", "C441", "B609", "LEG2", "BT36", "YK40", "TOBA", "BE55", "PZ04", "WT9", "L39", "C310", "PA20", "C56X", "E550", "CL35", "P180", "BE40", "YK18", "M20T", "PV1", "SH36", "P51", "T6", "SPIT", "C207", "PA28R", "A5", "PA34", "CHIN", "GL7T", "S92", "COL4", "PA46", "B462", "P46T", "LANC", "RV8", "G21", "AC68", "B429", "BN2P", "LJ35", "PA27", "TRIN", "UNIV", "AC90", "C402", "AN12", "HA4T", "MI8", "AN2", "GIV", "GLF4", "GLF2", "GLF6", "A210", "CAT", "CDC6", "PA38", "DO28", "GA5C", "B461", "B18T", "P28S", "C46", "EXPL", "B200", "DH2T", "AS21", "C68A", "PAY4", "B463", "PC24", "SLG2", "ASTO", "SP6", "SP7", "P166", "P66P", "P66T", "S360", "DC3T", "C77R", "E545", "FA5X", "G400", "S22T", "ECHO", "MJ5", "AC14", "C414", "MU2", "PA44", "SREY", "EFOX", "C185", "PAY3", "G115", "M200", "TB20", "P28T", "GLID", "P111", "SF25", "VW10", "P32R", "AP28", "DHC4", "A22", "PRPR", "D8", "DH3T", "BE99", "PA47", "AA5", "BDOG", "DV20", "A33");

# Try to put mil aircraft at mil spots
$milaircraft = array("F35", "T38", "F15", "F14", "F22", "F18", "A10", "F4", "C130", "B52", "B1", "B2", "CV22", "MV22", "V22", "H60", "CH47", "CH55", "C5", "C17", "C141", "EA6B", "A6", "P8", "P3", "P3C", "E3", "E3CF", "E3TF", "C97", "E6", "K35A", "K35E", "K35R", "KE3", "R135", "HAR", "E2", "C2", "B58", "EUFI", "SU11", "SU15", "SU17", "SU20", "SU22", "SU24", "SU25", "SU35", "SU30", "SU32", "SU34", "SU27", "MG29", "MG31", "E767", "U2", "SR71", "A4", "RQ1", "MQ9", "CH60", "H64", "H46", "H47", "H66", "F104", "F117", "VF35", "S3", "T33", "A7", "F8", "MIR2", "MIRA", "MIR4", "MRF1", "RFAL", "ETAR", "SMB2", "AJET", "F106", "F101", "MG21", "A400", "F18H", "VULC", "SUCO", "A50", "H53", "V35B", "C30J", "MH60", "TEX2", "F35A", "CNBR", "T160", "V10", "TOR", "AN22", "F5", "UH1Y", "AN32", "CN35", "AN26");

# For checking if it needs an S/H later
$supers = array("A225", "A380", "H4", "SLCH");
$heavies = array("B748", "B744", "B743", "B742", "B741", "B747", "A124", "C5", "A346", "A345", "A343", "A342", "A340", "B773", "B772", "B77F", "B77L", "B77W", "A359", "A35K", "A350", "MD11", "DC10", "MD10", "IL96", "IL86", "B788", "B789", "B78X", "B787", "L101", "B764", "B763", "B762", "B767", "E767", "KC46", "CONC", "A30B", "A306", "A3ST", "A300", "A310", "VC10", "B703", "B707", "DC86", "DC83", "A400");

# TODO: MAKE THIS SELECTABLE
$actoadd = 10;

$theseacs = array();

# Add this number of aircraft to list
for ($i=0; $i < $actoadd; $i++) {
  # Keep list of recently used spots to limited set
  if (count($usedspots) > 14) {
    # Remove first item in list (new ones are appended to bottom)
    array_splice($usedspots, 0, 1);
  }
  #
  $newfp = $flightplans[0];
  $nextfp = manglefp($newfp, $error_rates);
  $nextspot = usespot($newfp, $parkingspots);
  if ($nextspot != "") {
    if (in_array($usedspots, $nextspot)) {
      # Too recent, pick next spot in the same list
      # TODO: If it's small list it could still be too recent
      foreach (array($cargospots, $gaspots, $milspots, $otherspots) as &$thislist) {
        if (in_array($nextspot, $thislist)) {
          # Use next spot in this list
          $nextspot = $thislist[0];
          # Send this spot to bottom of list
          $thislist = loopiter($thislist);
        }
      }
    } else {
      # Not too recent, just move to bottom of list
      foreach (array($cargospots, $gaspots, $milspots, $otherspots) as &$thislist) {
        if (in_array($nextspot, $thislist)) {
          # move nextspot to end of thislist
          array_splice($thislist,array_search($nextspot,$thislist),1);
          $thislist[] = $nextspot;
        }
      }
    }
  } else {
    # Using random spot
    $airline = substr($newfp['callsign'],0,2);
    $aircraft = splittype($newfp['planned_aircraft'])[1];
    # Find best category and place it in the next spot there
    if ( (in_array($airline, $cargoairlines)) && ($cargospots != array()) ) {
      $nextspot = $cargospots[0];
      $cargospots = loopiter($cargospots);
    } elseif ( (in_array($aircraft, $gaaircraft)) && ($gaspots != array())) {
      $nextspot = $gaspots[0];
      $gaspots = loopiter($gaspots);
    } elseif ( (in_array($aircraft, $milaircraft)) && ($milspots != array())) {
      $nextspot = $milspots[0];
      $milspots = loopiter($milspots);
    } elseif ($otherspots != array()){
      $nextspot = $otherspots[0];
      $otherspots = loopiter($otherspots);
    } else {
      echo "<p>Could not find spot for ".$newfp['callsign']." type ".$newfp['planned_aircraft']."</p>";
    }
  }
  # Add this spot to bottom of the recently used spots list
  $usedspots[] = $nextspot;
  # Add this aircraft to the list of current aircraft
  $theseacs[] = array($nextfp, $nextspot);
  #echo "<p>Placed ".$nextfp[0]['callsign']." at ".$nextspot[0]."</p>";
  #echo "<p>".var_dump($nextspot)."</p>";
  # Put this FP at bottom of list, remove from top
  $flightplans = loopiter($flightplans);
  # Could write table here
}
# Path to output file
$outfile = "twrtrainer/temp.air";
# Create .air file with these aircraft
makeairfile($theseacs, $fieldelev, $outfile);

?>

<h2>Flight Plans from <?php echo $icao ?></h2>

<?php
$total = count($fps);
$calls = count($flightplans);
echo "<p>Found ".$total." flight plans and ".$calls." unique callsigns</p>";
# Not sure where this info is best printed
echo "<div class='pbox'><p>Parking spots available:</p>
      <table><tr><td>GA:</td><td>".count($gaspots)."</td></tr>
      <tr><td>Cargo:</td><td>".count($cargospots)."</td></tr>
      <tr><td>Mil:</td><td>".count($milspots)."</td></tr>
      <tr><td>Term:</td><td>".count($otherspots)."</td></tr></table></div>";
# array($csign, $actype, $dest, $alt, $rules, $rmks, $route);
?>
<div class="legend">
<h4 style="margin-bottom:0px;">Legend:</h4>
<p style="margin-top:0px;">Introduced errors in <span class="tdw">red</span>, existing errors in <span class="tdc">amber</span>. Hover over them <span class='tooltip warn'>liek dis<span class='tooltiptext'>like this</span></span> for more info.</p>
</div>
<div class="flighttable">
<table><tr><th>Round</th><th style="width:90px;">Callsign</th><th style="width:70px;">Type</th><th>Rules</th><th>Spot</th><th>Dest</th><th>Alt</th><th style="width:50%;">Route</th></tr>
<?php
# Get coordinates of departure airport for checking distances/directions
$origincoords = aptcoords($icao);
# Track item number
$i = 0;
# TODO: Track round
$round = 1;
foreach ($theseacs as $thisac) {
  #echo "<p>".var_dump($thisac[0][1][3])."</p>";

  # Span first column to indicate groups
  if ($i == 0) {
    echo "<tr><th rowspan='".count($theseacs)."'>".$round."</th>";
  } else {
    echo "<tr>";
  }

  # Callsign not touched
  echo "<td>".$thisac[0][0]['callsign']."</td>";


  # mangles: type, alt, dest, route, rules
  # Aircraft type
  $typefields = splittype($thisac[0][0]['planned_aircraft']);
  if ($thisac[0][1][0] != "") {
    # Process the mangled type field

    $wt = $typefields[0];
    $mwt = 1;
    if ($wt != "") {
      $wt = $wt . "/";
    } else {
      $wt = "&nbsp;&nbsp;";
    }
    if ($thisac[0][1][0][0] == 1) {
      # No previous pre, added one
      $ttw = "Added";
    } elseif ($thisac[0][1][0][0] == "") {
      $mwt = 0;
      $wtc = "";
    } else {
      # Changed existing pre
      #echo "<p>".var_dump($thisac[0][1][0])."</p>";
      $ttw = $thisac[0][1][0][0]."/";
    }
    if ($mwt == 1) {
      $wtc = "<div class='tooltip warn'>".$wt."<span class='tooltiptext'>".$ttw."</span></div>";
    }

    $ec = $typefields[2];
    $subc = " warn";
    if ($ec != "") {
      $ec = "/" . $ec;
    } else {
      $ec = "&nbsp;&nbsp;";
    }
    if ($thisac[0][1][0][2] == 1) {
      # No previous ec, added one
      $tte = "Added";
    } elseif ($thisac[0][1][0][2] == "") {
      $subc = " caut";
      $tte = "Missing";
    } else {
      # Changed existing ec
      $tte = "/".$thisac[0][1][0][2];
    }
    $ecc = "<div class='tooltip".$subc."'>".$ec."<span class='tooltiptext'>".$tte."</span></div>";

    $ac_cell = "<td>".$wtc.$typefields[1].$ecc;
  } else {
    # No tampering but we'll check it
    # TODO: Make weight check a function
    if (in_array($typefields[1], $heavies)) {
      if ( $typefields[0] != "H" ) {
        $ttw = "Heavy";
        if ($typefields[0] == "") {
          $wt = "&nbsp;&nbsp;";
        } else {
          $wt = $typefields[0] . "/";
        }
        $wtc = "<div class='tooltip caut'>".$wt."<span class='tooltiptext'>".$ttw."</span></div>";
      }
    } elseif (in_array($typefields[1], $supers)) {
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
      # All good for weight
      $wtc = "";
    }

    $commonec = array("L", "A", "G");
    if ($typefields[2] == "") {
      $ecc = "<div class='tooltip caut'>&nbsp;&nbsp;<span class='tooltiptext'>Missing</span></div>";
    } elseif (!in_array($typefields[2], $commonec)) {
      $ecc = "<div class='tooltip caut'>/".$typefields[2]."<span class='tooltiptext'>Strange</span></div>";
    } else {
      # TODO: Could get more involved here
      $ecc = "/".$typefields[2];
    }

    $ac_cell = "<td>".$wtc.$typefields[1].$ecc;
  }
  echo $ac_cell."</td>";


  # Flight type
  if ($thisac[0][1][4] != "") {
    $rules_cell = "<td class='tdw'><div class='tooltip'>".$thisac[0][0]['planned_flighttype']."<span class='tooltiptext'>".$thisac[0][1][4]."</span></div>";
  } else {
    $rules_cell = "<td>".$thisac[0][0]['planned_flighttype'];
  }
  echo $rules_cell."</td>";


  echo "<td>".$thisac[1][0]."</td>";


  # Destination
  # Whether direction of flight needs to be checked for this destination
  $check_dof = 1;
  if ($thisac[0][0]['planned_destairport'] != "" ) {
    if ($thisac[0][1][2] != "") {
      # Include original destination code
      $dest_cell = "<td class='tdw'><div class='tooltip'>".$thisac[0][0]['planned_destairport']."<span class='tooltiptext'>".$thisac[0][1][2]."</span></div>";
      $destcoords = aptcoords($thisac[0][1][2]);
    } else {
      # Not changed
      $dest_cell = "<td>".$thisac[0][0]['planned_destairport'];
      if ($thisac[0][0]['planned_destairport'] == $icao) {
        # Don't check DOF if it's returning here
        $check_dof = 0;
      } else {
        $destcoords = aptcoords($thisac[0][0]['planned_destairport']);
      }
    }
  } else {
    # Dest was blank
    $dest_cell = "<td>NONE";
    $check_dof = 0;
  }
  echo $dest_cell."</td>";


  # Altitude
  # Check altitude for direction of flight

  $alt = alt_to_int($thisac[0][0]['planned_altitude']);
  if ( ($check_dof == 1 ) && ($alt < 2500 + $fieldelev) ) {
    # DOF applies more than 3000 ft AGL - 14 CFR 91.159
    $check_dof = 0;
  } elseif ($check_dof == 1) {
    # echo "<p>Magvar: ".$magvar."</p>";
    $ihdg = inithdg($origincoords, $destcoords);
    # echo "<p>Init hdg: ".$ihdg."</p>";
    $dof = $ihdg + $magvar;
    # Loop to 360
    if ($dof < 0) {
      $dof = $dof + 360;
    } elseif ($dof > 360) {
      $dof = $dof - 360;
    }
  }
  # Check eastbounds
  if ( $check_dof == 1 && (($dof < 180 ) || ($dof == 360))) {
    if ( ($alt/1000)%2 != 1 ) {
      # Someone made an oopsie doopsie
      if ($thisac[0][1][1] != "") {
        # We made an oopsie doopsie
        $alt_cell = "<td class='tdw'><div class='tooltip'>".$alt."<span class='tooltiptext'>".$thisac[0][1][1]."</span></div>";
      } else {
        # Pilot made an oopsie doopsie
        # echo "<p>E brg to ".$thisac[0][0]['planned_destairport'].": ".$dof."</p>";
        $alt_cell = "<td class='tdc'><div class='tooltip'>".$alt."<span class='tooltiptext'>WAFDOF</span></div>";
      }
    } else {
      # All good
      $alt_cell = "<td>".$alt;
    }
  # Check westbounds
  } elseif ($check_dof == 1) {
    if ( ($alt/1000)%2 != 0 ) {
      # Someone made an oopsie doopsie
      if ($thisac[0][1][1] != "") {
        # We made an oopsie doopsie
        $alt_cell = "<td class='tdw'><div class='tooltip'>".$alt."<span class='tooltiptext'>".$thisac[0][1][1]."</span></div>";
      } else {
        # Pilot made an oopsie doopsie
        echo "<p>W brg to ".$thisac[0][0]['planned_destairport'].": ".$dof."</p>";
        $alt_cell = "<td class='tdc'><div class='tooltip'>".$alt."<span class='tooltiptext'>WAFDOF</span></div>";
      }
    } else {
      # All good
      $alt_cell = "<td>".$alt;
    }
  } else {
    # Don't check DOF
    $alt_cell = "<td>".$alt;
  }
  echo $alt_cell."</td>";


  # Route
  if ($thisac[0][1][3] != "") {
    # Route was changed
    //$mangled((0 nuke, >0 elems), origroute)
    if ($thisac[0][1][3][0] == 0) {
      # Whole route was changed
      if ($thisac[0][0]['planned_route'] == "") {
        $mangledpart = "<td class='tdw'><div class='tooltip'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;";
      } else {
        $mangledpart = "<td class='tdw'><div class='tooltip'>".$thisac[0][0]['planned_route'];
      }
      $therest = "";
    } else {
      # Part of route was changed
      $routeelems = multiexplode(array(" ","|","."),$thisac[0][0]['planned_route']);
      $mangledpart = "<td><div class='tooltip warn'>".implode(" ", array_slice($routeelems, 0, $thisac[0][1][3][0]));
      $therest = " ".implode(" ", array_slice($routeelems, $thisac[0][1][3][0]));
    }
    #echo "<p>".var_dump($thisac[0][1][3][1])."</p>";
    $route_cell = $mangledpart."<span class='tooltiptext'>".$thisac[0][1][3][1]."</span></div>".$therest;
  } else {
    # Nothing was touched
    # TODO: could be more rigorous
    $route_cell = "<td>".$thisac[0][0]['planned_route'];
  }
  echo $route_cell."</td></tr>\n";

  # On to the next one
  $i++;
}
 ?>
</table>
<!-- TODO: Make this actually do something -->
<form action=""><p>Get <input type="text" name="actoadd" style="width:20px;" value="<?php echo $actoadd ?>"/> more aircraft. <input type="submit" value="submit"></p>
</div>
</body>
</html>
