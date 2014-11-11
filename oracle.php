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
					} while ($id != ';');
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
						'implements' => $implements
					];
					if (!empty($extends)) {
						$parsed_extended_classes[$extends] = [
							'filename' => $this->filename,
							'extended_by' => $class_name,
							'implements' => $implements
						];
					}
					if (!empty($implements)) {
						$parsed_implemented_classes[$implements] = [
							'filename' => $this->filename,
							'implemented_by' => $class_name,
							'extends' => $extends
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
					} while ($id != ';');
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

					if ($functionName == "__construct") {
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
					} while ($id != ')');
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
					} while ($id != '{');
					$classBody = [$text];
					$curlyLevel = 1;
					do {
						list($id, $text) = $this->walk_next_token();
						if ($id == '{') {
							$curlyLevel++;
						}
						if ($id == '}') {
							$curlyLevel--;
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
			return array($token, $token);
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
			$this->for_idx++;
			if ($this->for_idx > 2) {
				$this->for_idx = 0;
			}
		}
		if ($this->for_idx === 0 || !$in_for) {
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
		if ($i === 99999) {
			$i = $this->ptr;
		}
		if ($prev) {
			while (--$i >= 0 && is_array($this->tkns[$i]) && $this->tkns[$i][0] === T_WHITESPACE);
		} else {
			while (++$i < sizeof($this->tkns) - 1 && is_array($this->tkns[$i]) && $this->tkns[$i][0] === T_WHITESPACE);
		}
		if (isset($this->tkns[$i]) && is_string($this->tkns[$i]) && $this->tkns[$i] === $token) {
			return $idx ? $i : true;
		} elseif (is_array($token) && isset($this->tkns[$i]) && is_array($this->tkns[$i])) {
			if (in_array($this->tkns[$i][0], $token)) {
				return $idx ? $i : true;
			} elseif ($prev && $this->tkns[$i][0] === T_OPEN_TAG) {
				return $idx ? $i : true;
			}
		}
		return false;
	}
	protected function prev_token() {
		$i = $this->ptr;
		while (--$i >= 0 && is_array($this->tkns[$i]) && $this->tkns[$i][0] === T_WHITESPACE);
		return $this->tkns[$i];
	}
	protected function walk_next_token() {
		$i = $this->ptr;
		$sizeof_tokens = sizeof($this->tkns);
		while (++$i <= $sizeof_tokens && is_array($this->tkns[$i]) && $this->tkns[$i][0] === T_WHITESPACE);
		$this->ptr = $i;
		if (!isset($this->tkns[$i])) {
			return null;
		}
		return $this->get_token($this->tkns[$i]);
	}
	protected function walk_next_token_ref(&$tokens, &$ptr) {
		$i = $ptr;
		$sizeof_tokens = sizeof($tokens);
		while (++$i <= $sizeof_tokens && is_array($tokens[$i]) && $tokens[$i][0] === T_WHITESPACE);
		$ptr = $i;
		if (!isset($tokens[$i])) {
			return null;
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
		for ($i = $i; $i >= 0; $i--) {
			$char = substr($haystack, $i, 1);
			if ($needle === $char) {
				$cnt++;
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
$fnDb = 'oracle.serialize';
if (!file_exists($fnDb) || 'flush' == $cmd) {
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
		$all_classes = array_merge_recursive($all_classes, $class);
		$all_extends = array_merge_recursive($all_extends, $extends);
		$all_implements = array_merge_recursive($all_implements, $implements);
		$all_methods = array_merge_recursive($all_methods, $methods);
	}
	fwrite(STDERR, "Serializing and storing..." . PHP_EOL);
	file_put_contents(
		$fnDb, serialize([
			'all_classes' => $all_classes,
			'all_extends' => $all_extends,
			'all_implements' => $all_implements,
			'all_methods' => $all_methods,
		])
	);
} else {
	if (time() - filemtime($fnDb) > 86400) {
		fwrite(STDERR, "Warning: database file older than a day" . PHP_EOL);
	}

	$db = unserialize(file_get_contents($fnDb));

	$all_classes = $db['all_classes'];
	$all_extends = $db['all_extends'];
	$all_implements = $db['all_implements'];
	$all_methods = $db['all_methods'];
}

function introspectInterface(&$found_implements) {
	if (is_array($found_implements['implemented_by'])) {
		foreach ($found_implements['implemented_by'] as $idx => $class_name) {
			echo "\t", $class_name, " - ", $found_implements["filename"][$idx], PHP_EOL;
		}
	} else {
		echo "\t", $found_implements['implemented_by'], ' - ', $found_implements["filename"], PHP_EOL;
	}
	echo PHP_EOL;
}
if ("implements" == $cmd) {
	if (!isset($all_implements[$argv[2]])) {
		fwrite(STDERR, "Interface not found: " . $argv[2] . PHP_EOL);
		exit(255);
	}
	echo $argv[2] . ' implemented by' . PHP_EOL;
	$found_implements = &$all_implements[$argv[2]];
	introspectInterface($found_implements);
}

function introspectExtends(&$found_extends) {
	foreach ($found_extends['extended_by'] as $idx => $class_name) {
		echo "\t", $class_name, " - ", $found_extends["filename"][$idx], PHP_EOL;
	}
	echo PHP_EOL;
}
if ("extends" == $cmd) {
	if (!isset($all_extends[$argv[2]])) {
		fwrite(STDERR, "Class not found: " . $argv[2] . PHP_EOL);
		exit(255);
	}
	$found_extends = &$all_extends[$argv[2]];
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
	if (!isset($argv[2]) || !isset($all_classes[$argv[2]])) {
		isset($argv[2]) && fwrite(STDERR, "Class not found: " . $argv[2] . PHP_EOL);
		fwrite(STDERR, 'Classes available:' . PHP_EOL . implode(PHP_EOL, array_keys($all_classes)) . PHP_EOL);
		exit(255);
	}
	$found_classes = &$all_classes[$argv[2]][0];
	echo $argv[2], PHP_EOL;
	introspectClass($found_classes);
}

if ("introspect" == $cmd) {
	$target = $argv[2];
	$strlenTarget = strlen($target);
	foreach ($all_implements as $k => $v) {
		if (substr($k, -$strlenTarget) == $target) {
			echo $k . ' implemented by' . PHP_EOL;
			$found_implements = &$all_implements[$k];
			introspectInterface($found_implements);
		}
	}
	foreach ($all_extends as $k => $v) {
		if (substr($k, -$strlenTarget) == $target) {
			$found_extends = &$all_extends[$k];
			echo $k . ' extended by' . PHP_EOL;
			introspectExtends($found_extends);
		}
	}
	foreach ($all_classes as $k => $v) {
		if (substr($k, -$strlenTarget) == $target) {
			$found_classes = &$all_classes[$k][0];
			echo "class " . $k, PHP_EOL;
			introspectClass($found_classes);
		}
	}
	ob_start();
	$foundMethod = false;
	foreach ($all_methods as $class => $methods) {
		foreach ($methods as $method) {
			if (substr($method[0], 0, strlen($target)) == $target) {
				$foundMethod = true;
				echo ' - ' . $class . '::' . $method[2], PHP_EOL;
			}
		}
	}
	$methodOutput = ob_get_clean();
	if ($foundMethod) {
		echo "Methods", PHP_EOL, $methodOutput;
	}
}

if ("calltip" == $cmd) {
	$target = $argv[2];
	$strlenTarget = strlen($target);
	ob_start();
	$foundMethod = false;
	foreach ($all_methods as $class => $methods) {
		foreach ($methods as $method) {
			if (substr($method[0], 0, strlen($target)) == $target) {
				$foundMethod = true;
				echo $class . '::' . $method[2], PHP_EOL;
				break 2;
			}
		}
	}
	$methodOutput = ob_get_clean();
	if ($foundMethod) {
		echo $methodOutput;
	}
}

if ("autocomplete" == $cmd) {
	$searchFor = $argv[2];
	$searchForLen = strlen($argv[2]);

	echo "term,match,class,type\n";

	$words = array_map(function ($v) {
		if (substr($v, 0, 1) == '\\') {
			$v = substr($v, 1);
		}
		return $v;
	}, array_keys($all_classes));
	sort($words);
	$words = array_unique(
		array_filter($words, function ($v) use ($searchFor) {
			return false !== stripos($v, $searchFor);
		})+
		array_filter($words, function ($v) use ($searchFor, $searchForLen) {
			return substr($v, 0, $searchForLen) == $searchFor;
		})
	);
	array_walk($words, function ($v) {
		$tmp = explode('\\', $v);
		fputcsv(STDOUT, [$v, array_pop($tmp), $v, 'class'], ',', '"');
	});

	foreach ($all_methods as $class => $methods) {
		foreach ($methods as $method) {
			if (false !== stripos($method[0], $searchFor) || substr($method[0], 0, $searchForLen) == $searchFor) {
				fputcsv(STDOUT, [$method[1], $method[2], $class, 'method'], ',', '"');
			}
		}
	}
}