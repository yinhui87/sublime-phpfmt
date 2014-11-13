# [php.fmt](https://github.com/dericofilho/php.tools) support for Sublime Text 2/3


php.fmt, php.tools and php.oracle aim to help PHP development. The following features are available through command palette (`ctrl+shift+P` or `cmd+shift+P`) :

 *  phpfmt: toggle format on save - handy if the code is small and you don't want to worry about formatting.
 *  phpfmt: format now - if format on save is disabled, you can manually format the code.
 *  phpfmt: format selection - formats only the selected code
 *  phpfmt: toggle auto align - it aligns vertically equals and fat arrow symbols
 *  phpfmt: toggle indent with space - for those who don't *like* indentation with tabs.
 *  phpfmt: toggle visibility order - ensure PSR2 §4.2. `[final|static] [private|protected|public] [$variable|function]...`
 *  phpfmt: getter and setter (snake_case) - analyses the classes in the file and add setters/getters - set_variable()/get_variable()
 *  phpfmt: getter and setter (camelCase) - analyses the classes in the file and add setters/getters - setVariable()/getVariable()
 *  phpfmt: getter and setter (Go) - analyses the classes in the file and add setters/getters - SetVariable()/Variable()
 *  phpfmt: toggle merge else+if into elseif - convert `...} else if (...` into `...} elseif( ...`
 *  phpfmt: toggle convert long array into short array - convert array(...) into [...] automatically
 *  phpfmt: toggle yoda mode - change automatically condition evaluations from `$a == CONST` to `CONST == $a`
 *  phpfmt: toggle automatic preincrement/predecrement - convert from `$a++` to `++$a`
 *  phpfmt: toggle smart linebreak after open curly - when adding missing curly blocks in codes, it adds an extra line break after first added curly token. Thus:
 <pre>
 if ($a) $b;
 </pre>
 to
 <pre>
 if ($a) {
     $b;
 }
 </pre>


Options which applies code analysis to work:

 *  phpfmt: build autocomplete database - analyse the code and generates a database used for autocomplete and automatic insertion of dependencies
 *  phpfmt: toggle autocomplete - GoSublime autocomplete style
 *  phpfmt: toggle dependency autoimport
 *  phpfmt: analyse this - analyse the current word, and seek for information such: class hierarchical data, implemented interfaces and methods.


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
<i>This can be enabled with the option "enable_auto_align"</i>
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
Prefer using the toggle options at command palette. However you might find yourself in need to setup where PHP is running, use this option below for the configuration file.
```
"php_bin":"/usr/local/bin/php",
```

### Troubleshooting
- If php errors appears make sure you can run PHP from the command line
