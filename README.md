# [php.fmt](https://github.com/dericofilho/php.tools) support for Sublime Text 2/3


php.fmt and php.tools aim to help PHP development. One of the features, code formatting, now is embeded too in ST3. For now it formats automatically when you save the PHP file.


### What does it do?
<table>
<tr>
<td>Before</td>
<td>After</td>
</tr>
<tr>
<td>
<pre><code>&lt;?php
for($i = 0; $i &lt; 10; $i++)
{
if($i%2==0)
echo "Flipflop";
}
</code></pre>
</td>
<td>
<pre><code>&lt;?php
for ($i = 0; $i &lt; 10; $i++) {
	if ($i%2 == 0) {
		echo "Flipflop";
	}
}
</code></pre>
</td>
</tr>
<tr>
<td>
<pre><code>&lt;?php
$a = 10;
$otherVar = 20;
$third = 30;
</code></pre>
</td>
<td>
<pre><code>&lt;?php
$a        = 10;
$otherVar = 20;
$third    = 30;
</code></pre>
<i>This can be disabled with the option "disable_auto_align"</i>
</td>
</tr>
<tr>
<td>
<pre><code>&lt;?php
namespace NS\Something;
use \OtherNS\C;
use \OtherNS\B;
use \OtherNS\A;
use \OtherNS\D;

$a = new A();
$b = new C();
$d = new D();
</code></pre>
</td>
<td>
<pre><code>&lt;?php
namespace NS\Something;

use \OtherNS\A;
use \OtherNS\C;
use \OtherNS\D;

$a = new A();
$b = new C();
$d = new D();
</code></pre>
<i>note how it sorts the use clauses, and removes unused ones</i>
</td>
</tr>
</table>

### What does it do? - PSR version
<table>
<tr>
<td>Before</td>
<td>After</td>
</tr>
<tr>
<td>
<pre><code>&lt;?php
for($i = 0; $i &lt; 10; $i++)
{
if($i%2==0)
echo "Flipflop";
}
</code></pre>
</td>
<td>
<pre><code>&lt;?php
for ($i = 0; $i &lt; 10; $i++) {
    if ($i%2 == 0) {
        echo "Flipflop";
    }
}
</code></pre>
<i>Note the identation of 4 spaces.</i>
</td>
</tr>
<tr>
<td>
<pre><code>&lt;?php
class A {
function a(){
return 10;
}
}
</code></pre>
</td>
<td>
<pre><code>&lt;?php
class A
{
    public function a()
    {
        return 10;
    }
}
</code></pre>
<i>Note the braces position, and the visibility adjustment in the method a().</i>
</td>
</tr>
<tr>
<td>
<pre><code>&lt;?php
namespace NS\Something;
use \OtherNS\C;
use \OtherNS\B;
use \OtherNS\A;
use \OtherNS\D;

$a = new A();
$b = new C();
$d = new D();
</code></pre>
</td>
<td>
<pre><code>&lt;?php
namespace NS\Something;

use \OtherNS\A;
use \OtherNS\C;
use \OtherNS\D;

$a = new A();
$b = new C();
$d = new D();
</code></pre>
<i>note how it sorts the use clauses, and removes unused ones</i>
</td>
</tr>
</table>

### Refactor
phpfmt's Refactor is a smart find&replace command which takes in consideration the context of the tokens. Therefore, it safely skips changes within strings or comment blocks.
- In Sublime Text press `ctrl+shift+P`
- Choose `phpfmt: refactor`
- Type the code which you want it to find.
- Type the code which you want it to replace with.

### Installation
####Requirements
- **You must have a running copy of PHP on the machine you are running Sublime Text**

Plugin runs better with PHP 5.5 or newer installed in the machine running the plugin. It works with PHP 5.4 if formatting only PHP 5.4 codes. *Do not attempt to format PHP 5.5 code with PHP 5.4 binary.*

####Install this plugin through Package Manager.
- In Sublime Text press `ctrl+shift+P`
- Choose `Package Control: Install Package`
- Choose `phpfmt`

####Configuration (Windows)
- Edit configuration file located at `%AppData%\Sublime Text 2\Packages\phpfmt\phpfmt.sublime-settings`
- For field `"php_bin"` enter the path to the php.exe
  Example: `"php_bin":"c:/PHP/php.exe"`

### Settings
```
"psr1":false,
"psr2":false,
"php_bin":"/usr/local/bin/php",
"indent_with_space":false,
// This allows you to invoke the formatter when you feel like it
"format_on_save":true
```

### Troubleshooting
- If php errors display make sure you can run PHP from the command line
