[![Puppet Forge Version](http://img.shields.io/puppetforge/v/herculesteam/augeasproviders_grub.svg)](https://forge.puppetlabs.com/herculesteam/augeasproviders_grub)
[![Puppet Forge Downloads](http://img.shields.io/puppetforge/dt/herculesteam/augeasproviders_grub.svg)](https://forge.puppetlabs.com/herculesteam/augeasproviders_grub)
[![Puppet Forge Endorsement](https://img.shields.io/puppetforge/e/herculesteam/augeasproviders_grub.svg)](https://forge.puppetlabs.com/herculesteam/augeasproviders_grub)
[![Build Status](https://img.shields.io/travis/hercules-team/augeasproviders_grub/master.svg)](https://travis-ci.org/hercules-team/augeasproviders_grub)
[![Coverage Status](https://img.shields.io/coveralls/hercules-team/augeasproviders_grub.svg)](https://coveralls.io/r/hercules-team/augeasproviders_grub)
[![Gemnasium](https://img.shields.io/gemnasium/hercules-team/augeasproviders_grub.svg)](https://gemnasium.com/hercules-team/augeasproviders_grub)


# grub: type/provider for grub files for Puppet

This module provides a new type/provider for Puppet to read and modify grub
config files using the Augeas configuration library.

The advantage of using Augeas over the default Puppet `parsedfile`
implementations is that Augeas will go to great lengths to preserve file
formatting and comments, while also failing safely when needed.

This provider will hide *all* of the Augeas commands etc., you don't need to
know anything about Augeas to make use of it.

## Requirements

Ensure both Augeas and ruby-augeas 0.3.0+ bindings are installed and working as
normal.

See [Puppet/Augeas pre-requisites](http://docs.puppetlabs.com/guides/augeas.html#pre-requisites).

## Installing

On Puppet 2.7.14+, the module can be installed easily ([documentation](http://docs.puppetlabs.com/puppet/latest/reference/modules_installing.html)):

    puppet module install herculesteam/augeasproviders_grub

You may see an error similar to this on Puppet 2.x ([#13858](http://projects.puppetlabs.com/issues/13858)):

    Error 400 on SERVER: Puppet::Parser::AST::Resource failed with error ArgumentError: Invalid resource type `kernel_parameter` at ...

Ensure the module is present in your puppetmaster's own environment (it doesn't
have to use it) and that the master has pluginsync enabled.  Run the agent on
the puppetmaster to cause the custom types to be synced to its local libdir
(`puppet master --configprint libdir`) and then restart the puppetmaster so it
loads them.

## Compatibility

### Puppet versions

Minimum of Puppet 2.7.

### Augeas versions

Augeas Versions           | 0.10.0  | 1.0.0   | 1.1.0   | 1.2.0   |
:-------------------------|:-------:|:-------:|:-------:|:-------:|
**PROVIDERS**             |
kernel\_parameter (grub)  | **yes** | **yes** | **yes** | **yes** |
kernel\_parameter (grub2) | **yes** | **yes** | **yes** | **yes** |

## Documentation and examples

Type documentation can be generated with `puppet doc -r type` or viewed on the
[Puppet Forge page](http://forge.puppetlabs.com/herculesteam/augeasproviders_grub).


### kernel_parameter provider

This is a custom type and provider supplied by `augeasproviders`.  It supports
both GRUB Legacy (0.9x) and GRUB 2 configurations.

#### manage parameter without value

    kernel_parameter { "quiet":
      ensure => present,
    }

#### manage parameter with value

    kernel_parameter { "elevator":
      ensure  => present,
      value   => "deadline",
    }

#### manage parameter with multiple values

    kernel_parameter { "rd_LVM_LV":
      ensure  => present,
      value   => ["vg/lvroot", "vg/lvvar"],
    }

#### manage parameter on certain boot types

Bootmode defaults to "all", so settings are applied for all boot types usually.

Apply only to the default boot:

    kernel_parameter { "quiet":
      ensure   => present,
      bootmode => "default",
    }

Apply only to normal boots. In GRUB legacy, normal boots consist of the default boot plus non-recovery ones. In GRUB2, normal bootmode is just an alias for default.

    kernel_parameter { "quiet":
      ensure   => present,
      bootmode => "normal",
    }

Only recovery mode boots (unsupported with GRUB 2):

    kernel_parameter { "quiet":
      ensure   => present,
      bootmode => "recovery",
    }

#### delete entry

    kernel_parameter { "rhgb":
      ensure => absent,
    }

#### manage parameter in another config location

    kernel_parameter { "elevator":
      ensure => present,
      value  => "deadline",
      target => "/mnt/boot/grub/menu.lst",
    }


## Issues

Please file any issues or suggestions [on GitHub](https://github.com/hercules-team/augeasproviders_grub/issues).
