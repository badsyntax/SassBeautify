# SassBeautify

A Sublime Text plugin that beautifies Sass files. (Compatible with Sublime Text 2 & 3.)

![ScreenShot](https://raw.github.com/badsyntax/SassBeautify/master/screenshot.png)

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

## Settings

Once installed, you can customize how the conversion works by changing the package settings.

1. Open the default settings from the preferences menu: `Preferences >> Package Settings >> SassBeautify >> Settings - Default`
2. Copy the settings and paste them into your user settings file: `Preferences >> Package Settings >> SassBeautify >> Settings - User`
3. Change the user settings.

### Settings overview

The following settings can be adjusted:

```javascript
{
  "indent": 4,        // How many spaces to use for each level of indentation. "t" means use hard tabs.
  "dasherize": false, // Convert underscores to dashes
  "old": false,       // Output the old-style ":prop val" property syntax. Only meaningful when generating Sass.
  "path": false       // Custom path to your sass bin folder (eg: "/home/richard/.rvm/.../gems/sass-3.2.9/bin")
}
```

## How it works

This plugin is simply a wrapper around the `sass-convert` utility. The `sass-convert `utility will *compile your Sass/Scss
to Sass/Scss*, and thus there's a chance values might change. (For example, see [issue #7](https://github.com/badsyntax/SassBeautify/issues/7).) 

## Issues

This plugin should work on Linux (tested on Ubuntu 12.04), Windows (tested on Windows 7) and OSX (tested on 10.5.7).
Please [create an issue](https://github.com/badsyntax/SassBeautify/issues) if you find it doesn't work
as expected on your setup.

## License

Licensed under the MIT license. Created by [Richard Willis](http://badsyntax.co/)
