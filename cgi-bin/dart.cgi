#!/usr/bin/perl -w
use strict;
use CGI qw(:standard);
use CGI::Carp qw ( fatalsToBrowser ); 
use DBI;
use lib "lib/";
use lib "lib/pangu";
use pangu;
use userCookie;

my $userCookie = new userCookie;
my $userId = (cookie('cid')) ? $userCookie->checkCookie(cookie('cid')) : 0;
if(!$userId)
{
	print header;
	print <<eof;
	<h2>Error</h2>
	Please <a onclick="openDialog('login.cgi');">login</a> first!
	<script type="text/javascript">
		openDialog('login.cgi');
		loadingHide();
	</script>
eof
    exit;
}

my $commoncfg = readConfig("main.conf");
my $dbh=DBI->connect("DBI:mysql:$commoncfg->{DATABASE}:$commoncfg->{DBHOST}",$commoncfg->{USERNAME},$commoncfg->{PASSWORD});

undef $/;# enable slurp mode
my $html = <DATA>;

my $darts = '';
my $allDart=$dbh->prepare("SELECT * FROM matrix WHERE container Like 'dart'");
$allDart->execute();
while (my @allDart = $allDart->fetchrow_array())
{
	$allDart[8] = escapeHTML($allDart[8]);
	$allDart[8] =~ s/\n/<br>/g;

	$darts = "<form id='dartList$$' name='dartList$$'>
		<table id='darts$$' class='display' style='width: 100%;'>
			<thead>
				<tr>
					<th style='text-align:left'><b>DArT</b></th>
					<th style='text-align:left'><b>SNPs</b></th>
					<th style='text-align:left'><b>Genotypes</b></th>
					<th style='text-align:left'><b>Creator</b></th>
					<th style='text-align:left'><b>Creation Date</b></th>
				</tr>
			</thead>
			<tbody>" unless($darts);
	$darts .= "<tr>
		<td title='Dart'><a id='dartId$allDart[0]$$' onclick='openDialog(\"dartView.cgi?dartId=$allDart[0]\")' title='View'>$allDart[2]</a></td>
		<td title='Click to download DArT Report'><a href='download.cgi?dartId=$allDart[0]' target='hiddenFrame'>$allDart[3]</a></td>
		<td title='Click to download DArT Report'><a href='download.cgi?dartId=$allDart[0]' target='hiddenFrame'>$allDart[4]</a></td>
		<td title='Creator'>$allDart[9]</td>
		<td title='Creation date'>$allDart[10]</td>
		</tr>";
}
$darts .= "</tbody></table></form>\n" if($darts);
my $button = "<div class='ui-state-highlight ui-corner-all' style='padding: 0 .7em;'>
	<button style='float: right; margin-top: .3em; margin-right: .3em;' onclick='openDialog(\"dartNew.cgi\")'>New DArT Report</button>
	<button style='float: right; margin-top: .3em; margin-right: .3em;' onclick='refresh(\"general\")'>Refresh</button>
	";
$button .= "<h2>DArT Reports</h2>";

unless($darts)
{
	$button .= "<p class='ui-state-error ui-corner-all' style='padding: .7em;'><span class='ui-icon ui-icon-alert' style='float: left; margin-right: .3em;'></span>
			<strong>No DArT Report, please upload one!</strong></p>";
}
$button .= "</div>\n";

$html =~ s/\$button/$button/g;
$html =~ s/\$darts/$darts/g;
$html =~ s/\$\$/$$/g;


print header(-cookie=>cookie(-name=>'general',-value=>5));
print $html;

__DATA__
$button
$darts
<script>
buttonInit();
$( "#darts$$" ).dataTable({
	"scrollY": "600px",
	"scrollCollapse": true,
	"paging": false
});
loadingHide();
</script>