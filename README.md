# SassBeautify

https://sublime.wbond.net/packages/SassBeautify

A Sublime Text plugin that beautifies Sass files. (Compatible with Sublime Text 2 & 3.)

![ScreenShot](https://raw.github.com/badsyntax/SassBeautify/master/assets/screenshot.png)

## Dependencies

This plugin uses `sass-convert`, and so you need to have sass installed. Read the [sass download page](http://sass-lang.com/download.html) to view the installation options.

It's a good idea to always use the latest version of Sass.

## Installation

**Option 1 (recommended)**

Install via package control:

1. Ensure you have package control installed, see here: https://sublime.wbond.net/installation
2. Install the package: open up the command palette (ctrl/cmd + shift + p), execute the following command:
'Package Control: Install Package', then enter 'SassBeautify'

**Option 2**

Manual download:

1. Download the zip file file here: https://github.com/badsyntax/SassBeautify/archive/master.zip
2. Unzip the archive, rename the 'SassBeautify-master' folder to 'SassBeautify' and move it into your Sublime Text 'Packages' directory.

## Usage

**Default usage**

Run the plugin from the command palette:

1. Open the command palette (ctrl/cmd + shift + p)
2. Enter 'SassBeautify'

**Conversion usage**

Run the conversion commands from the command palette:

1. Open the command palette (ctrl/cmd + shift + p)
2. Type 'SassBeautify'
3. Choose one of the following options:
  * Convert from CSS to current type
  * Convert from SCSS to current type
  * Convert from SASS to current type

## Settings

Once installed, you can customize how the beautification works by changing the package settings.

1. Open the default settings from the preferences menu: `Preferences >> Package Settings >> SassBeautify >> Settings - Default`
2. Copy the settings and paste them into your user settings file: `Preferences >> Package Settings >> SassBeautify >> Settings - User`
3. Change the user settings.

### Settings overview

The following settings can be adjusted:

```javascript
{
  // How many spaces to use for each level of indentation. "t" means use hard tabs.
  "indent": 4,
  // Convert underscores to dashes.
  "dasherize": false,
  // Output the old-style ":prop val" property syntax. Only meaningful when generating Sass.
  "old": false,
  // Custom environment PATH.
  "path": false,
  // Custom environment GEM_PATH.
  "gemPath": false,
  // Beautify the sass file after saving it?
  "beautifyOnSave": false,
  // Keep "inline" comments inline?
  "inlineComments": false,
  // Add a new line between selectors?
  "newlineBetweenSelectors": false,
  // Use single quotes everywhere
  "useSingleQuotes": false
}
```

### Key bindings

The plugin does not set any default key bindings, thus you will need to specify your own.

In your keymap file (Preferences >> Key bindings - User), add a custom key binding:

```json
[
    {
        "keys": ["alt+w"],
        "command": "sass_beautify"
    }
]
```


## Issues with ruby, Sass and your PATH

If you installed ruby and sass via a version manager tool like [RVM](https://rvm.io/), [rbenv](https://github.com/sstephenson/rbenv) or via an installer like [ruby installer](http://rubyinstaller.org/), then you're likely to encounter issues with running `sass-convert` from Sublime Text. 

### Compatibility with RVM/rbenv

You need to specify the custom `PATH` and `GEM_PATH `values in your SassBeautify user settings.

Follow the steps below:

1. Open up terminal
2. Run: `echo $PATH`
3. Copy the *entire* `PATH` into the 'path' setting
4. Run: `echo $GEM_PATH`
5. Copy the *entire* `GEM_PATH` into the 'gemPath' setting

### Compatibility with RubyInstaller

During the install process, there should be an option to add ruby to your environment PATH. Ensure this option is selected.

## Issues

This plugin should work on Linux (tested on Ubuntu 12.04), Windows (tested on Windows 7/8) and OSX (tested on 10.5.7).

Please [create an issue](https://github.com/badsyntax/SassBeautify/issues) if you find it doesn't work as expected on your setup.

## Thanks

Thanks to the [contributors](https://github.com/badsyntax/SassBeautify/graphs/contributors) and to all the people 
who have tested and reported issues.

## License

Licensed under the MIT license. Created by [Richard Willis](http://badsyntax.co/)
