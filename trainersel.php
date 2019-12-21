<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>TWRTrainer Generator</title>
<meta name="description" content="TWRTrainer Generator">
<meta name="author" content="N">
<link rel="stylesheet" href="style.css">
<style>
.rates {
  width: 40px;
  float: right;
}

.sub {
  padding-left:15px;
}
</style>
<script type="text/javascript">
function load_gnd() {
  document.getElementById("chance_ec").value = "0.5";
  document.getElementById("chance_alt").value = "0.25";
  document.getElementById("chance_dest").value = "0.01";
  document.getElementById("chance_route").value = "0.25";
  document.getElementById("chance_rules").value = "0.1";
  document.getElementById("chance_route_swap").value = "0.1";
  document.getElementById("chance_route_dct").value = "0.05";
  document.getElementById("chance_route_blk").value = "0.05";
}
function load_twr() {
  document.getElementById("chance_ec").value = "0.01";
  document.getElementById("chance_alt").value = "0.01";
  document.getElementById("chance_dest").value = "0.001";
  document.getElementById("chance_route").value = "0.01";
  document.getElementById("chance_rules").value = "0.01";
  document.getElementById("chance_route_swap").value = "0.1";
  document.getElementById("chance_route_dct").value = "0.05";
  document.getElementById("chance_route_blk").value = "0.05";
}
</script>
</head>
<body>
<h2>Select an airport:</h2>
<form method="post" id="gen_form" action="/twrtrainerapt.php">
<p>
<?php
# Whitelisting these, could also scan existing files
$airports = array("KSEA", "KPDX", "KTTD", "KHIO", "KOTH");

foreach ($airports as $airport) {
  if (file_exists("twrtrainer/".$airport.".apt")) {
    if ($airport == "KPDX") {
      $chk = ' checked="checked"';
    } else {
      $chk = '';
    }
    echo '<input type="radio" name="icao" value="'.$airport.'"'.$chk.'/> '.$airport.'<br/>';
  }
}
?>
</p>
<p>Initial number of aircraft: <input type="text" name="actoadd" style="width:20px;" value="5"/></p>

<h3>Error Rates</h3>
<p>
<input type="button" name="gnd_em" id="gnd_em" value="Load GND emphasis" onclick="load_gnd()"/>
<input type="button" name="twr_em" id="twr_em" value="Load TWR emphasis" onclick="load_twr()"/>
</p>
<!--<p style="width:200px;">-->
<!-- TODO: Loop this -->
<table>
<tr><th>Type</th><th>Rate/1</th></tr>
<tr><td>Equipment code:</td><td><input type="text" name="chance_ec" id="chance_ec" value="0.5" class="rates"/></td></tr>
<tr><td>Altitude:</td><td><input type="text" name="chance_alt" id="chance_alt" value="0.25" class="rates"/></td></tr>
<tr><td>Destination:</td><td><input type="text" name="chance_dest" id="chance_dest" value="0.01" class="rates"/></td></tr>
<tr><td>Flight rules:</td><td><input type="text" name="chance_rules"  id="chance_rules" value="0.1" class="rates"/></td></tr>
<tr><td>Route:</td><td><input type="text" name="chance_route" id="chance_route" value="0.25" class="rates"></td/></tr>
<!--<p style="padding-left:20px;">-->
<tr><td class="sub">Total swap:</td><td><input type="text" name="chance_route_swap" id="chance_route_swap" value="0.1" class="rates"/></td></tr>
<tr><td class="sub">DCT:</td><td><input type="text" name="chance_route_dct" id="chance_route_dct" value="0.05" class="rates"/></td></tr>
<tr><td class="sub">Blank:</td><td><input type="text" name="chance_route_blk" id="chance_route_blk" value="0.05" class="rates"/></td></tr>
</table>
<p><input type="submit" value="Generate Aircraft"></p>
</form>

</body>
</html>
