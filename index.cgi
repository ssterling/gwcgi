#!/usr/bin/env perl
# gwcgi - CGI web interface for Greasweazle
# Copyright 2022 Seth Price, all rights reserved.

use strict;
use warnings;
use utf8;
use feature 'signatures';

use open ":std", ":encoding(UTF-8)";

use Sys::Hostname;
use Tie::IxHash;
use Config::Tiny;

# printed below
my $version = '0.2.0';

# Grab configuration file
my $config = Config::Tiny->new;
if (-e './config.ini') {
	$config = Config::Tiny->read('./config.ini');
} else {
	# TODO: log warning that config file does not exist
	$config = Config::Tiny->read('./config.ini.sample');
}

# Shorthand for hash that gets parsed in insertion order
sub oh(%)
{
	tie my %hash => 'Tie::IxHash';
	%hash = @_;
	\%hash
}

# For templates below; really only used for filter selection
my @valid_tags = (
	['8'], ['5.25'], ['3.5'],
	['common','Common formats'],
	['ibmpc','IBM PC (&amp; compat.)'],
	['mac','Macintosh'],
	['pc98','NEC PC-98 series'],
	['apple','Apple II/III'],
	['commodore','Commodore 8-bit'],
	['amiga','Amiga'],
	['atari','Atari'],
	['dec','DEC (PDP-11)'],
	['ibm','IBM midrange computers']
);

# Default values for given disk types
my @templates = (
	### 8″
	{name => '8″ SD-77-1 / single-density, 74 tracks per side, single-sided',
		cylinders => '0-73', heads => '0', steps => '1',
		formats => oh('IBM'=>'237.25KB'),
		tags => ['8', 'ibm'],
		value => '8-SD-74-1'},
	{name => '8″ SD-77-1 / single-density, 77 tracks per side, single-sided',
		cylinders => '0-76', heads => '0', steps => '1',
		formats => oh('PC-98'=>'250.25KB', 'DEC'=>'250KB'),
		tags => ['8', 'pc98', 'dec'],
		value => '8-SD-77-1'},
	{name => '8″ SD-77-2 / single-density, 74 tracks per side, double-sided',
		cylinders => '0-73', heads => '0-1', steps => '1',
		formats => oh('IBM'=>'500.5KB'),
		tags => ['8', 'ibm'],
		value => '8-SD-74-2'},
	{name => '8″ DD-77-1 / double-density, 77 tracks per side, single-sided',
		cylinders => '0-76', heads => '0', steps => '1',
		formats => oh('DEC'=>'500KB'),
		tags => ['8', 'dec'],
		value => '8-DD-77-1'},
	{name => '8″ DD-74-2 / double-density, 74 tracks per side, double-sided',
		cylinders => '0-73', heads => '0-1', steps => '1',
		formats => oh('IBM'=>'980KB/1200KB'),
		tags => ['8', 'ibm'],
		value => '8-DD-74-2'},
	{name => '8″ DD-77-2 / double-density, 77 tracks per side, double-sided',
		cylinders => '0-76', heads => '0-1', steps => '1',
		formats => oh('PC-98'=>'1232KB'),
		tags => ['8', 'pc98'],
		value => '8-DD-77-2'},
	### 5¼″
	{name => '5¼″ SD-40-1 / single-density, 40 tracks per side, single-sided',
		cylinders => '0-39', heads => '0', steps => '2',
		formats => oh('Osborne'=>'100KB', 'Atari'=>'90KB/130KB'),
		tags => ['5.25', 'atari'],
		value => '5.25-SD-40-1'},
	{name => '5¼″ DD-35-1 / double-density, 35 tracks per side, single-sided',
		cylinders => '0-34', heads => '0', steps => '2',
		formats => oh('Apple II'=>'113.75KB/140KB', 'Commodore'=>'170KB'),
		tags => ['5.25', 'common', 'apple', 'commodore'],
		value => '5.25-DD-35-1'},
	{name => '5¼″ DD-35-2 / double-density, 35 tracks per side, double-sided',
		cylinders => '0-34', heads => '0-1', steps => '2',
		formats => oh('Commodore'=>'340KB'),
		tags => ['5.25', 'commodore'],
		value => '5.25-DD-35-2'},
	{name => '5¼″ DD-40-1 / double-density, 40 tracks per side, single-sided',
		cylinders => '0-39', heads => '0', steps => '2',
		formats => oh('PC'=>'180KB', 'Atari'=>'180KB'),
		tags => ['5.25', 'ibmpc', 'atari'],
		value => '5.25-DD-40-1'},
	{name => '5¼″ DD-40-2 / double-density, 40 tracks per side, double-sided',
		cylinders => '0-39', heads => '0-1', steps => '2',
		formats => oh('PC'=>'360KB', 'Amiga'=>'440KB', 'Atari'=>'360KB'),
		tags => ['5.25', 'common', 'ibmpc', 'amiga', 'atari'],
		value => '5.25-DD-40-2'},
	{name => '5¼″ QD-77-1 / quad-density, 77 tracks per side, single-sided',
		cylinders => '0-76', heads => '0', steps => '1',
		formats => oh('Commodore'=>'521KB'),
		tags => ['5.25', 'commodore'],
		value => '5.25-QD-77-1'},
	{name => '5¼″ QD-77-2 / quad-density, 77 tracks per side, double-sided',
		cylinders => '0-76', heads => '0-1', steps => '1',
		formats => oh('Commodore'=>'1042KB'),
		tags => ['5.25', 'commodore'],
		value => '5.25-QD-77-2'},
	{name => '5¼″ QD-80-1 / quad-density, 80 tracks per side, single-sided',
		cylinders => '0-79', heads => '0', steps => '1',
		formats => oh('PC'=>'320KB', 'DEC'=>'400KB'),
		tags => ['5.25', 'ibmpc', 'dec'],
		value => '5.25-QD-80-1'},
	{name => '5¼″ QD-80-2 / quad-density, 80 tracks per side, double-sided',
		cylinders => '0-79', heads => '0-1', steps => '1',
		formats => oh('PC'=>'640KB/720KB', 'PC-98'=>'640KB/720KB', 'Amiga'=>'880KB'),
		tags => ['5.25', 'ibmpc', 'amiga'],
		value => '5.25-QD-80-2'},
	{name => '5¼″ HD-77-2 / high-density, 77 tracks per side, double-sided',
		cylinders => '0-76', heads => '0-1', steps => '1',
		formats => oh('PC-98'=>'1232KB'),
		tags => ['5.25', 'pc98'],
		value => '5.25-HD-77-2'},
	{name => '5¼″ HD-80-2 / high-density, 80 tracks per side, double-sided',
		cylinders => '0-79', heads => '0-1', steps => '1',
		formats => oh('PC'=>'1.2MB'),
		tags => ['5.25', 'common', 'ibmpc'],
		value => '5.25-HD-80-2'},
	### 3½″
	{name => '3½″ DD-40-1 / double-density, 40 tracks per side, single-sided',
		cylinders => '0-39', heads => '0', steps => '2',
		formats => oh('Brother WP/LW series'=>'120KB'),
		tags => ['3.5'],
		value => '3.5-DD-40-1'},
	{name => '3½″ DD-40-2 / double-density, 40 tracks per side, single-sided',
		cylinders => '0-39', heads => '0-1', steps => '2',
		formats => oh('Brother WP/LW series'=>'240KB'),
		tags => ['3.5'],
		value => '3.5-DD-40-2'},
	{name => '3½″ DD-80-1 / double-density, 80 tracks per side, single-sided',
		cylinders => '0-79', heads => '0', steps => '1',
		formats => oh('PC'=>'320KB/360KB', 'Macintosh'=>'400KB', 'Apple II'=>'400KB', 'Atari'=>'360KB'),
		tags => ['3.5', 'ibmpc', 'mac', 'apple', 'atari'],
		value => '3.5-DD-80-1'},
	{name => '3½″ DD-80-2 / double-density, 80 tracks per side, double-sided',
		cylinders => '0-79', heads => '0-1', steps => '1',
		formats => oh('PC'=>'640KB/720KB', 'PC-98'=>'640KB/720KB', 'Macintosh'=>'800KB', 'Apple II'=>'800KB', 'Amiga'=>'880KB', 'Atari'=>'720KB'),
		tags => ['3.5', 'common', 'ibmpc', 'mac', 'apple', 'pc98', 'amiga', 'atari'],
		value => '3.5-DD-80-2'},
	{name => '3½″ HD-80-2 / high-density, 80 tracks per side, double-sided',
		cylinders => '0-79', heads => '0-1', steps => '1',
		formats => oh('PC'=>'1.44MB/1.68MB', 'PC-98'=>'1.2MB/1.44MB', 'Macintosh'=>'1.44MB', 'Apple II'=>'1.44MB', 'Amiga'=>'1.52MB/1.76MB', 'Atari'=>'1.44MB'),
		tags => ['3.5', 'common', 'ibmpc', 'mac', 'apple', 'amiga', 'pc98', 'atari'],
		value => '3.5-HD-80-2'},
	{name => '3½″ HD-82-2 / high-density, 82 tracks per side, double-sided',
		cylinders => '0-81', heads => '0-1', steps => '1',
		formats => oh('PC'=>'1.72MB'),
		tags => ['3.5', 'ibmpc'],
		value => '3.5-HD-82-2'},
	{name => '3½″ ED-80-2 / extended-density, 82 tracks per side, double-sided',
		cylinders => '0-79', heads => '0-1', steps => '1', # practically just an alias for HD-80-2
		formats => oh('PC'=>'2.88MB'),
		tags => ['3.5', 'ibmpc'],
		value => '3.5-ED-80-2'},
);

# Returns array of templates with given value
sub get_templates_with_given_tag($tag)
{
	my @templates_ret = ();
	foreach my $template (@templates) {
		if (grep /^$tag$/, @{$template->{tags}}) {
			push @templates_ret, $template;
		}
	}
	return @templates_ret;
}

# Prints a combobox ‘<option>…</option>’ for each template
sub print_template_options_with_given_tag($tag, $indent_level)
{
	foreach my $template (get_templates_with_given_tag($tag)) {
		my $title = '';
		my @keys = keys %{$template->{formats}};
		for (my $i; $i <= $#keys; $i++) {
			$title .= ', ' unless $i == 0;
			$title .= "$keys[$i] $template->{formats}{$keys[$i]}";
		}
		print "\t" x $indent_level;
		print "<option value=\"$template->{value}\" id=\"$template->{value}\" title=\"$title\">$template->{name}</option>\n";
	}
}

print 'Content-Type: text/html; charset=UTF8

<!DOCTYPE html>
<html>
	<head>
		<title>gwcgi</title>
		<meta name="robots" content="noindex">
		<style type="text/css">
			fieldset
			{
				width: 600px;
				max-width: 600px;
			}
			select#template,
			select#template optgroup,
			select#template option
			{
				width: 500px;
			}
		</style>
		<script type="text/javascript">
			/* procedurally generated */
			function on_append_change()
			{' . "
				if (document.getElementById('template-show-format').checked) {
";
foreach my $template (@templates) {
	my $inner = $template->{name};
	my @keys = keys %{$template->{formats}};
	if (keys %{$template->{formats}}) {
		$inner .= ' [';
		for (my $i = 0; $i <= $#keys; $i++) {
			$inner .= ', ' unless $i == 0;
			$inner .= "$keys[$i] $template->{formats}{$keys[$i]}";
		}
		$inner .= ']';
	}
	print "\t\t\t\t\tdocument.getElementById('$template->{value}').innerHTML = '$inner';\n";
}
print '				} else {
';
foreach my $template (@templates) {
	print "\t\t\t\t\tdocument.getElementById('$template->{value}').innerHTML = '$template->{name}';\n";
}
print "				}
			}

			function setValuesWhereNotLocked(cylinders, heads, steps, params)
			{
				if (!document.getElementById('cylinders-lock').checked) {
					document.getElementById('cylinders').value = cylinders;
				}
				if (!document.getElementById('heads-lock').checked) {
					document.getElementById('heads').value = heads;
				}
				if (!document.getElementById('steps-lock').checked) {
					document.getElementById('steps').value = steps;
				}
				if (!document.getElementById('params-lock').checked) {
					document.getElementById('ts-params').value = params;
				}
			}

			/* procedurally generated */
			function on_template_select()
			{
				if (document.getElementById('template').selectedIndex == 0) {
					setValuesWhereNotLocked('', '', '', '');
";
foreach my $template (@templates) {
	print "\t\t\t\t} else if (document.getElementById('template').value == '$template->{value}') {
					setValuesWhereNotLocked('$template->{cylinders}', '$template->{heads}', '$template->{steps}', '$template->{tsparams}');
";
}
print '				}
			}

			/* procedurally generated */
			function on_filter_select()
			{' . "
				if (document.getElementById('template-filter').selectedIndex == 0) {
					var optgroups = document.getElementById('template').children;
					for (var i = 0; i < optgroups.length; i++) {
						var options = optgroups[i].children;
						for (var j = 0; j < options.length; j++) {
							options[j].hidden = false;
						}
					}
";
foreach my $tag (@valid_tags) {
	print "\t\t\t\t} else if (document.getElementById('template-filter').value == '$tag->[0]') {
					var optgroups = document.getElementById('template').children;
					for (var i = 0; i < optgroups.length; i++) {
						var options = optgroups[i].children;
						for (var j = 0; j < options.length; j++) {
							options[j].hidden = true;
						}
					}
";
	foreach my $template (@templates) {
		if (grep /^$tag->[0]$/, @{$template->{tags}}) {
			print "\t\t\t\t\tdocument.getElementById('$template->{value}').hidden = false;\n";
		}
	}
}
print "				}
			}

			function log(msg)
			{
				var ta = document.getElementById('cmd_output');
				ta.value += msg + '\\n';
				ta.scrollTop = ta.scrollHeight;
			}

			function changeStatus(msg)
			{
				document.getElementById('status').innerHTML = msg;
			}

			function fieldIsEmpty(id)
			{
				return (document.getElementById(id).value.trim().length ? false : true);
			}

			function valueOf(id)
			{
				return document.getElementById(id).value.trim();
			}

			function radioValue(name)
			{
				var eles = document.getElementsByName(name);
				for (var i = 0; i < eles.length; i++) {
					if (eles[i].checked) {
						return eles[i].value;
					}
				}
			}

			var sock; /* Websocket */

			function startCommand()
			{
				changeStatus('Attempting connection…');
				sock = new WebSocket('ws://$config->{websocket}->{address}:$config->{websocket}->{port}/');

				sock.onopen = function() { 
					changeStatus('Connected');

					var params = '';
					changeStatus('Calculating parameters client-side');
					params += '--drive ' + radioValue('drive');
					if (!fieldIsEmpty('cylinders') || !fieldIsEmpty('heads') || !fieldIsEmpty('steps')) {
						params += ' --tracks ';
						var put_colon = false;
						if (!fieldIsEmpty('cylinders')) {
							params += 'c=' + valueOf('cylinders');
							put_colon = true;
						}
						if (!fieldIsEmpty('heads')) {
							if (put_colon) {
								params += ':';
							}
							params += 'h=' + valueOf('heads');
							put_colon = true;
						}
						if (!fieldIsEmpty('steps')) {
							if (put_colon) {
								params += ':';
							}
							params += 'step=' + valueOf('steps');
						}
						if (!fieldIsEmpty('ts-params')) {
							if (put_colon) {
								params += ':';
							}
							params += valueOf('ts-params');
						}
					}
					params += ' --revs ' + valueOf('revs');
					if (!fieldIsEmpty('params')) {
						params += ' ' + valueOf('params');
					}

					changeStatus('Sending parameters to server');
					log('>> ' + params);
					sock.send(params);
					changeStatus('Connected');
				};

				sock.onclose = function() { 
					changeStatus('Disconnected');
				};

				sock.onmessage = function(event) {
					if (event.data.startsWith('[DOWNLOAD]')) {
						var e = document.createElement('a');
						e.setAttribute('href', event.data.substring(10));
						if (valueOf('filename') != '') {
							e.setAttribute('download', valueOf('filename') + '.scp');
						}
						document.body.appendChild(e);
						e.click();
						document.body.removeChild(e);
					} else {
						log(event.data);
					}
				};
			}

		" . '</script>
	</head>
	<body>
		<h1>gwcgi</h1>
		<p>Host: <code>' . hostname . '</code><br>Version: ' . $version . '</p>

		<form action="javascript:void(0);" onsubmit="return false;">
			<fieldset>
				<legend>Device</legend>
				<label for="device">Device:</label>
				<input type="text" id="device" name="device" value="' . $config->{_}->{device} . '" disabled>
				<br>
				Drive:
				<input type="radio" id="drive_a" name="drive" value="A" checked><label for="drive_a">A</label>
				<input type="radio" id="drive_b" name="drive" value="B"><label for="drive_b">B</label>
				<input type="radio" id="drive_0" name="drive" value="0"><label for="drive_0">0</label>
				<input type="radio" id="drive_1" name="drive" value="1"><label for="drive_1">1</label>
				<input type="radio" id="drive_2" name="drive" value="2"><label for="drive_2">2</label><!--
				<br>
				<label for="flippy">Flippy-modded:</label><input type="checkbox" id="flippy">-->
			</fieldset>
			<fieldset>
				<noscript><p style="font-weight:bold;">Template functionality will not work without JavaScript</p></noscript>
				<legend>Trackset</legend>
				<label for="template">Template:</label>
				<select id="template" name="template" onChange="on_template_select()">
					<option value="0" selected>— None —</option>
					<optgroup label="8″ (8-inch)">
';
print_template_options_with_given_tag('8', 6);
print '					</optgroup>
					<optgroup label="5¼″ (5.25-inch)">
';
print_template_options_with_given_tag('5.25', 6);
print '					</optgroup>
					<optgroup label="3½″ (3.5-inch)">
';
print_template_options_with_given_tag('3.5', 6);
print '					</optgroup>
				</select>
				<br>
				<input type="checkbox" id="template-show-format" onChange="on_append_change()">
				<label for="template-show-format">Append filesystem sizes to template name</label>
				<br>
				<label for="template-filter">Filter templates by tag:</label>
				<select id="template-filter" name="template-filter" onChange="on_filter_select()">
					<option value="0" selected>— None —</option>
';
foreach my $tag (@valid_tags) {
	print "\t\t\t\t\t<option value=\"$tag->[0]\">$tag->[1]</option>\n" unless $tag->[0] =~ /^[\d\.]+$/;
}
print '
				</select>
				<hr>
				<label for="cylinders">Cylinders:</label>
				<input type="text" id="cylinders" name="c" placeholder="0 = first cylinder">
				<input type="checkbox" id="cylinders-lock"><label for="cylinders-lock">Lock value</label>
				<br>
				<label for="heads">Heads:</label>
				<input type="text" id="heads" name="h" placeholder="generally: 0, 1, or 0-1">
				<input type="checkbox" id="heads-lock"><label for="heads-lock">Lock value</label>
				<br>
				<label for="steps">Steps:</label>
				<input type="text" id="steps" name="step" placeholder="generally: 1, or 2">
				<input type="checkbox" id="steps-lock"><label for="steps-lock">Lock value</label>
				<br>
				<label for="ts-params">Additional parameters:</label>
				<input type="text" id="ts-params" name="ts-params" placeholder="colon-seperated">
				<input type="checkbox" id="params-lock"><label for="">Lock value</label>
			</fieldset>
			<fieldset>
				<legend>Additional parameters</legend>
				<label for="revs">Revolutions per track:</label>
				<input type="number" id="revs" name="revs" min="1" value="1">
				<br>
				<label for="params">Additional parameters:</label>
				<input type="text" id="params" name="params">
				<br>
				<label for="filename">Output filename:</label>
				<input type="text" id="filename" name="filename" maxlength="128" placeholder="leave blank for default">.scp
			</fieldset>
			<br>
			<button onclick="startCommand();">Read disk</button>
		</form>
		<hr>
		<output>
			<textarea id="cmd_output" readonly cols="80" rows="10"></textarea>
			<p>Status: <span id="status">Not yet connected</span></p>
		</output>
		<script type="text/javascript">
			/* Populate fields */
			on_append_change();
			on_template_select();
			on_filter_select();
		</script>
	</body>
</html>';

#
# LE FORK
# Basically: invoke websocketd if not already up
#

my $pidf = fork;
if ($pidf != 0) {
	# This is the parent, and the page is output, so exit
	exit 0;
}

my $pidfile_loc = '/tmp/gwcgi-websocketd.pid';
if (not -e $pidfile_loc) {
	# We ended up creating the file, so just write current PID
	open FP, '>', $pidfile_loc;
	print FP $$;
	close FP;
} else {
	open FP, '<', $pidfile_loc or die $!;
	my $pid = <FP>;
	close FP;
	my $killstat = kill(0, $pid);
	if ($$ eq $pid or $killstat ne 0) {
		# Already running; quit
		exit 0;
	} else {
		truncate $pidfile_loc, 0 or die $!;  # remove contents
		open FP, '>', $pidfile_loc;
		print FP $$;
		close FP;
	}
}

system("websocketd --loglevel=fatal --port $config->{websocket}->{port} ./gw-wrapper.sh");
# TODO: some way to kill the daemon later on

1;
