<?php

class ClassParser extends Parser {
	private function detectsNamespace() {
		$namespace = '';
		while (list($index, $token) = each($this->tkns)) {
			list($id, $text) = $this->get_token($token);
			$this->ptr = $index;
			switch ($id) {
				case T_NAMESPACE:
					do {
						list($id, $text) = $this->walk_next_token();
						if (T_WHITESPACE === $id) {
							continue;
						}
						$namespace .= $text;
					} while (';' != $id);
					break 2;
			}
		}
		$namespace = substr($namespace, 0, -1) . '\\';
		return $namespace;
	}
	public function parse($source) {
		$parsed_classes = [];
		$parsed_extended_classes = [];
		$parsed_implemented_classes = [];
		$this->tkns = token_get_all($source);
		$this->code = '';

		$namespace = $this->detectsNamespace();
		reset($this->tkns);
		while (list($index, $token) = each($this->tkns)) {
			list($id, $text) = $this->get_token($token);
			$this->ptr = $index;
			switch ($id) {
				case T_CLASS:
					if ($this->is_token([T_DOUBLE_COLON], true)) {
						continue;
					}
					$class_name = null;
					$extends = null;
					$implements = null;
					// Seek for class name
					list($id, $text) = $this->walk_next_token();
					$class_name = $text;

					list($id, $text) = $this->walk_next_token();
					if (T_EXTENDS == $id) {
						list($id, $text) = $this->walk_next_token();
						$extends = $text;
					}

					if (T_IMPLEMENTS == $id) {
						list($id, $text) = $this->walk_next_token();
						$implements = $text;
					}

					$this->debug('[' . $class_name . ' e:' . $extends . ' i:' . $implements . ']');
					$parsed_classes[$namespace . $class_name][] = [
						'filename' => $this->filename,
						'extends' => $extends,
						'implements' => $implements,
					];
					if (!empty($extends)) {
						$parsed_extended_classes[$extends] = [
							'filename' => $this->filename,
							'extended_by' => $class_name,
							'implements' => $implements,
						];
					}
					if (!empty($implements)) {
						$parsed_implemented_classes[$implements] = [
							'filename' => $this->filename,
							'implemented_by' => $class_name,
							'extends' => $extends,
						];
					}
					break;
			}
		}
		return [
			$parsed_classes,
			$parsed_extended_classes,
			$parsed_implemented_classes,
		];
	}
}

class ClassMethodParser extends Parser {
	private function detectsNamespace() {
		$namespace = '';
		while (list($index, $token) = each($this->tkns)) {
			list($id, $text) = $this->get_token($token);
			$this->ptr = $index;
			switch ($id) {
				case T_NAMESPACE:
					do {
						list($id, $text) = $this->walk_next_token();
						if (T_WHITESPACE === $id) {
							continue;
						}
						$namespace .= $text;
					} while (';' != $id);
					break 2;
			}
		}
		$namespace = substr($namespace, 0, -1) . '\\';
		return $namespace;
	}
	private function parseMethods($namespace, $className, $tokens) {
		$ptr = 0;
		$methodList = [];
		while (list($index, $token) = each($tokens)) {
			list($id, $text) = $this->get_token($token);
			$ptr = $index;
			switch ($id) {
				case T_FUNCTION:
					list($id, $text) = $this->walk_next_token_ref($tokens, $ptr);
					if ('(' == $text) {
						break;
					}
					if (T_STRING == $id) {
						$functionName = $text;
					}

					if ("__construct" == $functionName) {
						$functionName = $className;
						$functionCall = $className;
						$functionSignature = $className;
					} else {
						$functionCall = $functionName;
						$functionSignature = $functionName;
					}
					do {
						list($id, $text) = $this->walk_next_token_ref($tokens, $ptr);
						if (T_VARIABLE == $id) {
							$functionSignature .= ' ';
							$functionCall .= ' ';
						}
						if (T_VARIABLE == $id || ',' == $text || '(' == $text || ')' == $text) {
							$functionCall .= $text;
						}
						$functionSignature .= $text;
					} while (')' != $id);
					$methodList[] = [
						$functionName,
						str_replace('( ', '(', $functionCall),
						str_replace('( ', '(', $functionSignature),
					];
					break;
			}
		}
		return $methodList;
	}
	public function parse($source) {
		$this->tkns = token_get_all($source);
		$this->code = '';

		$foundMethods = [];
		$namespace = $this->detectsNamespace();
		reset($this->tkns);
		while (list($index, $token) = each($this->tkns)) {
			list($id, $text) = $this->get_token($token);
			$this->ptr = $index;
			switch ($id) {
				case T_CLASS:
					if ($this->is_token([T_DOUBLE_COLON], true)) {
						continue;
					}

					list($id, $text) = $this->walk_next_token();
					$className = $text;
					do {
						list($id, $text) = $this->walk_next_token();
					} while ('{' != $id);
					$classBody = [$text];
					$curlyLevel = 1;
					do {
						list($id, $text) = $this->walk_next_token();
						if ('{' == $id) {
							++$curlyLevel;
						}
						if ('}' == $id) {
							--$curlyLevel;
						}
						$classBody[] = [$id, $text];
					} while ($curlyLevel > 0);
					$foundMethods[$namespace . $className] = $this->parseMethods($namespace, $className, $classBody);
					break;
			}
		}
		return $foundMethods;
	}
}

abstract class Parser {
	protected $filename = '';
	protected $debug = '';
	protected $indent_size = 1;
	protected $indent_char = "\t";
	protected $block_size = 1;
	protected $new_line = "\n";
	protected $indent = 0;
	protected $for_idx = 0;
	protected $code = '';
	protected $ptr = 0;
	protected $tkns = 0;
	public function __construct($filename, $debug) {
		$this->filename = $filename;
		$this->debug = $debug;
	}
	abstract public function parse($source);
	protected function get_token($token) {
		if (is_string($token)) {
			return [$token, $token];
		} else {
			return $token;
		}
	}
	protected function append_code($code = "", $trim = true) {
		if ($trim) {
			$this->code = rtrim($this->code) . $code;
		} else {
			$this->code .= $code;
		}
	}
	protected function get_crlf_indent($in_for = false, $increment = 0) {
		if ($in_for) {
			++$this->for_idx;
			if ($this->for_idx > 2) {
				$this->for_idx = 0;
			}
		}
		if (0 === $this->for_idx || !$in_for) {
			return $this->get_crlf() . $this->get_indent($increment);
		} else {
			return $this->get_space(false);
		}
	}
	protected function get_crlf($true = true) {
		return $true ? $this->new_line : "";
	}
	protected function get_space($true = true) {
		return $true ? " " : "";
	}
	protected function get_indent($increment = 0) {
		return str_repeat($this->indent_char, ($this->indent + $increment) * $this->indent_size);
	}
	protected function set_indent($increment) {
		$this->indent += $increment;
		if ($this->indent < 0) {
			$this->indent = 0;
		}
	}
	protected function inspect_token($delta = 1) {
		if (!isset($this->tkns[$this->ptr + $delta])) {
			return [null, null];
		}
		return $this->get_token($this->tkns[$this->ptr + $delta]);
	}
	protected function is_token($token, $prev = false, $i = 99999, $idx = false) {
		if (99999 === $i) {
			$i = $this->ptr;
		}
		if ($prev) {
			while (--$i >= 0 && is_array($this->tkns[$i]) && T_WHITESPACE === $this->tkns[$i][0]);
		} else {
			while (++$i < sizeof($this->tkns) - 1 && is_array($this->tkns[$i]) && T_WHITESPACE === $this->tkns[$i][0]);
		}
		if (isset($this->tkns[$i]) && is_string($this->tkns[$i]) && $this->tkns[$i] === $token) {
			return $idx ? $i : true;
		} elseif (is_array($token) && isset($this->tkns[$i]) && is_array($this->tkns[$i])) {
			if (in_array($this->tkns[$i][0], $token)) {
				return $idx ? $i : true;
			} elseif ($prev && T_OPEN_TAG === $this->tkns[$i][0]) {
				return $idx ? $i : true;
			}
		}
		return false;
	}
	protected function prev_token() {
		$i = $this->ptr;
		while (--$i >= 0 && is_array($this->tkns[$i]) && T_WHITESPACE === $this->tkns[$i][0]);
		return $this->tkns[$i];
	}
	protected function walk_next_token() {
		$i = $this->ptr;
		$sizeof_tokens = sizeof($this->tkns);
		while (++$i <= $sizeof_tokens && is_array($this->tkns[$i]) && T_WHITESPACE === $this->tkns[$i][0]);
		$this->ptr = $i;
		if (!isset($this->tkns[$i])) {
			return;
		}
		return $this->get_token($this->tkns[$i]);
	}
	protected function walk_next_token_ref(&$tokens, &$ptr) {
		$i = $ptr;
		$sizeof_tokens = sizeof($tokens);
		while (++$i <= $sizeof_tokens && is_array($tokens[$i]) && T_WHITESPACE === $tokens[$i][0]);
		$ptr = $i;
		if (!isset($tokens[$i])) {
			return;
		}
		return $this->get_token($tokens[$i]);
	}
	protected function has_ln_after() {
		$id = null;
		$text = null;
		list($id, $text) = $this->inspect_token();
		return T_WHITESPACE === $id && substr_count($text, PHP_EOL) > 0;
	}
	protected function has_ln_before() {
		$id = null;
		$text = null;
		list($id, $text) = $this->inspect_token(-1);
		return T_WHITESPACE === $id && substr_count($text, PHP_EOL) > 0;
	}
	protected function has_ln_prev_token() {
		list($id, $text) = $this->get_token($this->prev_token());
		return substr_count($text, PHP_EOL) > 0;
	}
	protected function substr_count_trailing($haystack, $needle) {
		$cnt = 0;
		$i = strlen($haystack) - 1;
		for ($i = $i; $i >= 0; --$i) {
			$char = substr($haystack, $i, 1);
			if ($needle === $char) {
				++$cnt;
			} elseif (' ' !== $char && "\t" !== $char) {
				break;
			}
		}
		return $cnt;
	}
	protected function debug($msg) {
		$this->debug && fwrite(STDERR, $msg . PHP_EOL);
	}
}

if (!isset($argv[1])) {
	exit(255);
}
$cmd = trim(strtolower($argv[1]));
$ignoreList = [];
$ignoreListFn = 'oracle.ignore';
if (file_exists($ignoreListFn)) {
	$ignoreList = file($ignoreListFn);
}
$fnDb = 'oracle.sqlite';
if (!file_exists($fnDb) || 'flush' == $cmd) {
	file_exists($fnDb) && unlink($fnDb);
	$db = new SQLite3($fnDb);
	$db->exec(
		'CREATE TABLE classes (
			filename text,
			class text,
			extends text,
			implements text
		);'
	);
	$db->exec(
		'CREATE TABLE extends (
			filename text,
			extends text,
			extended_by text,
			implements text
		);'
	);
	$db->exec(
		'CREATE TABLE implements (
			filename text,
			implements text,
			implemented_by text,
			extends text
		);'
	);
	$db->exec(
		'CREATE TABLE methods (
			filename text,
			class text,
			method_name text,
			method_call text,
			method_signature text
		);'
	);

	fwrite(STDERR, "Database not found... generating" . PHP_EOL);
	$debug = false;
	$uri = $argv[2];

	$dir = new RecursiveDirectoryIterator($uri);
	$it = new RecursiveIteratorIterator($dir);
	$files = new RegexIterator($it, '/^.+\.php$/i', RecursiveRegexIterator::GET_MATCH);
	$all_classes = [];
	$all_extends = [];
	$all_implements = [];
	$all_methods = [];
	foreach ($files as $file) {
		$file = $file[0];
		foreach ((array) $ignoreList as $ignore) {
			$ignore = trim($ignore);
			if (
				substr(str_replace(getcwd() . '/', '', $file), 0, strlen($ignore)) == $ignore ||
				substr($file, 0, strlen($ignore)) == $ignore
			) {
				continue 2;
			}
		}
		echo $file, PHP_EOL;

		$content = file_get_contents($file);

		list($class, $extends, $implements) = (new ClassParser($file, $debug))->parse($content);
		$methods = (new ClassMethodParser($file, $debug))->parse($content);

		foreach ($class as $class_name => $class_data) {
			foreach ($class_data as $data) {
				$db->exec('
				INSERT INTO
					classes
				VALUES
					(
						"' . SQLite3::escapeString($file) . '",
						"' . SQLite3::escapeString($class_name) . '",
						"' . SQLite3::escapeString($data['extends']) . '",
						"' . SQLite3::escapeString($data['implements']) . '"
					);
				');
			}
		}

		foreach ($extends as $extends_name => $data) {
			$db->exec('
				INSERT INTO
					extends
				VALUES
					(
						"' . SQLite3::escapeString($file) . '",
						"' . SQLite3::escapeString($extends_name) . '",
						"' . SQLite3::escapeString($data['extended_by']) . '",
						"' . SQLite3::escapeString($data['implements']) . '"
					);
			');
		}

		foreach ($implements as $implements_name => $data) {
			$db->exec('
				INSERT INTO
					implements
				VALUES
					(
						"' . SQLite3::escapeString($file) . '",
						"' . SQLite3::escapeString($implements_name) . '",
						"' . SQLite3::escapeString($data['implemented_by']) . '",
						"' . SQLite3::escapeString($data['extends']) . '"
					);
			');
		}

		foreach ($methods as $class => $class_methods) {
			foreach ($class_methods as $data) {
				$db->exec("
				INSERT INTO
					methods
				VALUES
					(
						'" . SQLite3::escapeString($file) . "',
						'" . SQLite3::escapeString($class) . "',
						'" . SQLite3::escapeString($data[0]) . "',
						'" . SQLite3::escapeString($data[1]) . "',
						'" . SQLite3::escapeString($data[2]) . "'
					);
				");
			}
		}
	}
	$db->close();
	exit(0);
}
if (time() - filemtime($fnDb) > 86400) {
	fwrite(STDERR, "Warning: database file older than a day" . PHP_EOL);
}

$db = new SQLite3($fnDb);

function introspectInterface(&$found_implements) {
	foreach ($found_implements as $row) {
		echo "\t", $row['implemented_by'], " - ", $row["filename"], PHP_EOL;
	}
	echo PHP_EOL;
}
if ("implements" == $cmd) {
	$results = $db->query("SELECT * FROM implements WHERE implements = '" . SQLite3::escapeString($argv[2]) . "'");
	$found_implements = [];
	while ($row = $results->fetchArray()) {
		$found_implements[] = [
			'filename' => $row['filename'],
			'implemented_by' => $row['implemented_by'],
		];
	}
	if (empty($found_implements)) {
		fwrite(STDERR, "Interface not found: " . $argv[2] . PHP_EOL);
		exit(255);
	}
	echo $argv[2] . ' implemented by' . PHP_EOL;
	introspectInterface($found_implements);
}

function introspectExtends(&$found_extends) {
	foreach ($found_extends as $row) {
		echo "\t", $row['extended_by'], " - ", $row["filename"], PHP_EOL;
	}
	echo PHP_EOL;
}
if ("extends" == $cmd) {
	$results = $db->query("SELECT * FROM extends WHERE extends = '" . SQLite3::escapeString($argv[2]) . "'");
	$found_extends = [];
	while ($row = $results->fetchArray()) {
		$found_extends[] = [
			'filename' => $row['filename'],
			'extended_by' => $row['extended_by'],
		];
	}
	if (empty($found_extends)) {
		fwrite(STDERR, "Class not found: " . $argv[2] . PHP_EOL);
		exit(255);
	}

	echo $argv[2] . ' extended by' . PHP_EOL;
	introspectExtends($found_extends);
}

function introspectClass(&$found_classes) {
	if (!empty($found_classes['extends'])) {
		echo "\t extends ", $found_classes['extends'], PHP_EOL;
	}

	if (!empty($found_classes['implements'])) {
		echo "\t implements ", $found_classes['implements'], PHP_EOL;
	}

	echo PHP_EOL;
}
if ("class" == $cmd) {
	$results = $db->query("SELECT * FROM classes WHERE class LIKE '%" . SQLite3::escapeString($argv[2]) . "'");
	$found_classes = [];
	while ($row = $results->fetchArray()) {
		$found_classes = [
			'filename' => $row['filename'],
			'class' => $row['class'],
			'extends' => $row['extends'],
			'implements' => $row['implements'],
		];
		break;
	}

	if (empty($found_classes)) {
		fwrite(STDERR, "Class not found: " . $argv[2] . PHP_EOL);
		exit(255);
	}

	echo $argv[2], PHP_EOL;
	introspectClass($found_classes);
}

if ("introspect" == $cmd) {
	$target = $argv[2];

	$results = $db->query("SELECT * FROM implements WHERE implements = '%" . SQLite3::escapeString($target) . "'");
	$all_found_implements = [];
	while ($row = $results->fetchArray()) {
		$all_found_implements[$row['implements']][] = [
			'filename' => $row['filename'],
			'implemented_by' => $row['implemented_by'],
		];
	}
	foreach ($all_found_implements as $implements => $found_implements) {
		echo $implements . ' implemented by' . PHP_EOL;
		introspectInterface($found_implements);
	}

	$results = $db->query("SELECT * FROM extends WHERE extends = '%" . SQLite3::escapeString($target) . "'");
	$all_found_extends = [];
	while ($row = $results->fetchArray()) {
		$all_found_extends[$row['extends']][] = [
			'filename' => $row['filename'],
			'extended_by' => $row['extended_by'],
		];
	}
	foreach ($all_found_extends as $extends => $found_extends) {
		echo $extends . ' extended by' . PHP_EOL;
		introspectExtends($found_extends);
	}

	$results = $db->query("SELECT * FROM classes WHERE class LIKE '%" . SQLite3::escapeString($target) . "'");
	while ($row = $results->fetchArray()) {
		$found_classes = [[
			'filename' => $row['filename'],
			'class' => $row['class'],
			'extends' => $row['extends'],
			'implements' => $row['implements'],
		]];
		echo "class " . $row['class'], PHP_EOL;
		introspectClass($found_classes);
	}

	ob_start();
	$foundMethod = false;
	$results = $db->query("SELECT * FROM methods WHERE method_name LIKE '%" . SQLite3::escapeString($target) . "'");
	while ($row = $results->fetchArray()) {
		$foundMethod = true;
		echo ' - ' . $row['class'] . '::' . $row['method_signature'], PHP_EOL;
	}
	$methodOutput = ob_get_clean();
	if ($foundMethod) {
		echo "Methods", PHP_EOL, $methodOutput;
	}
}

if ("calltip" == $cmd) {
	ob_start();
	$foundMethod = false;
	$results = $db->query("SELECT * FROM methods WHERE method_name LIKE '%" . SQLite3::escapeString($argv[2]) . "'");
	while ($row = $results->fetchArray()) {
		$foundMethod = true;
		echo $row['class'] . '::' . $row['method_signature'], PHP_EOL;
		break;
	}
	$methodOutput = ob_get_clean();
	if ($foundMethod) {
		echo $methodOutput;
	}
}

if ("autocomplete" == $cmd) {
	$searchFor = $argv[2];

	echo "term,match,class,type\n";

	$results = $db->query("SELECT * FROM classes WHERE class LIKE '%" . SQLite3::escapeString($searchFor) . "%' ORDER BY class");
	while ($row = $results->fetchArray()) {
		$tmp = explode('\\', $row['class']);
		fputcsv(STDOUT, [$row['class'], array_pop($tmp), $row['class'], 'class'], ',', '"');
	}
	$results = $db->query("SELECT * FROM classes WHERE class LIKE '%" . SQLite3::escapeString($searchFor) . "' ORDER BY class");
	while ($row = $results->fetchArray()) {
		$tmp = explode('\\', $row['class']);
		fputcsv(STDOUT, [$row['class'], array_pop($tmp), $row['class'], 'class'], ',', '"');
	}
	$results = $db->query("SELECT * FROM methods WHERE method_name LIKE '%" . SQLite3::escapeString($searchFor) . "%'");
	while ($row = $results->fetchArray()) {
		fputcsv(STDOUT, [$row['method_call'], $row['method_signature'], $row['class'], 'method'], ',', '"');
	}
}