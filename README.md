# SassBeautify

A basic Sublime Text 2 plugin that beautifies Sass (or Scss) files.

## Dependencies

You need to have the 'sass-convert' executable installed on your system to use this plugin.
(If you have Sass installed on your system, then you should have sass-convert.)

## Installation

**Option 1 (recommended)**

Install via package control:

1. Ensure you have package control installed, see here: http://wbond.net/sublime_packages/package_control
2. Install the package: open up the command palette (ctrl + shift + p), execute the following command:
'Package Control: Install Package', then enter 'SassBeautify'

**Option 2**

Manual download:

1. Download the zip file file here: https://github.com/badsyntax/SassBeautify/archive/master.zip
2. Unzip the archive, rename the 'SassBeautify-master' folder to 'SassBeautify' and move it into your
Sublime Text 'Packages' directory.

## Usage

Run the plugin from the command palette:

1. Open the command palette (ctrl + shift + p)
2. Enter 'SassBeautify'

**Note:** Expect the plugin to run slow the first time you run it.

## Settings

Once installed, you can customize how the conversion works by changing the package settings.

1. Open the default settings from the preferences menu: `Preferences >> Package Settings >> SassBeautify >> Settings - Default`
2. Copy the settings and paste them into your user settings file: `Preferences >> Package Settings >> SassBeautify >> Settings - User`
3. Change the settings!

### Settings overview

The following settings can be adjusted:

```javascript
{
  "indent": 4,        // How many spaces to use for each level of indentation. "t" means use hard tabs.
  "dasherize": false, // Convert underscores to dashes
  "old": false        // Output the old-style ":prop val" property syntax. Only meaningful when generating Sass.
}
```

## Issues

This plugin should work on Linux (tested on Ubuntu), Windows (tested on Windows 7) and OSX (tested on 10.5.7).
Please [create an issue](https://github.com/badsyntax/SassBeautify/issues) if you find it doesn't work
as expected on your setup.

## License

Licensed under the MIT license. Created by [Richard Willis](http://badsyntax.co/)
