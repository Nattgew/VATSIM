<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>TWRTrainer Generator</title>
<meta name="description" content="TWRTrainer Generator">
<meta name="author" content="N">
<!--<link rel="stylesheet" href="style.css">-->
<style>
.rates {
  width: 40px;
  float: right;
}

.sub {
  padding-left:15px;
}
</style>
<script>

document.getElementById("mytext").value = "My value";
</script>
</head>
<h2>Select an airport:</h2>

<p>
<input type="radio" name="icao" value="KPDX" checked="checked"/> KPDX<br/>
<input type="radio" name="icao" value="KSEA"/> KSEA<br/>
<input type="radio" name="icao" value="KOTH"/> KOTH
</p>

<h3>Error Rates</h3>
<p>
<input type="button" name="gnd_em" value="Load GND emphasis"> <input type="button" name="twr_em" value="Load TWR emphasis"> 
</p>
<!--<p style="width:200px;">-->
<!-- TODO: Loop this -->
<form action="" name="prob_form">
<table>
<tr><th>Type</th><th>Rate/1</th></tr>
<tr><td>Equipment code:</td><td><input type="text" name="chance_ec" id="chance_ec" value="0.5" class="rates"/></td></tr>
<tr><td>Altitude:</td><td><input type="text" name="chance_alt" id="chance_alt" value="0.25" class="rates"/></td></tr>
<tr><td>Destination:</td><td><input type="text" name="chance_dest" id="chance_dest" value="0.01" class="rates"/></td></tr>
<tr><td>Flight rules:</td><td><input type="text" name="chance_rules" name="chance_rules" value="0.1" class="rates"/></td></tr>
<tr><td>Route:</td><td><input type="text" name="chance_route" value="0.25" class="rates"></td/></tr>
<!--<p style="padding-left:20px;">-->
<tr><td class="sub">Total swap:</td><td><input type="text" name="chance_route_swap" value="0.1" class="rates"/></td></tr>
<tr><td class="sub">DCT:</td><td><input type="text" name="chance_route_dct" value="0.05" class="rates"/></td></tr>
<tr><td class="sub">Blank:</td><td><input type="text" name="chance_route_blk" value="0.05" class="rates"/></td></tr>
</table>
<p><input type="submit" value="Generate Aircraft">
</p>
</form>
</body>
</html>
