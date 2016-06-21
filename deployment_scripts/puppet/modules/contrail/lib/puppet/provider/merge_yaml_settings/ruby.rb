require 'yaml'

Puppet::Type.type(:merge_yaml_settings).provide(:ruby) do
    desc "Support for merging yaml configuration files."

    def create
        merged_settings = get_merged_settings
        write_to_file(@resource[:path], merged_settings.to_yaml.gsub( "x5c", "\\" )) if not (merged_settings.empty?)
    end

    def destroy
        File.unlink(@resource[:path])
    end

    def exists?
        get_dict(@resource[:sample_settings]) == get_merged_settings
    end

    def get_merged_settings
        sample_settings = get_dict(@resource[:sample_settings])
        override_settings = get_dict(@resource[:override_settings])
        sample_settings.deep_merge(override_settings)
    end

    def write_to_file(filename, content)
        debug "writing content #{content} to the file #{filename}"
        begin
          File.open(filename, "w") { |f| f.puts content }
        rescue
          raise Puppet::Error, "merge_yaml_settings: the file #{filename} can not be written!"
        end
    end

    def get_dict(obj)
        return obj if obj.is_a?(Hash)
        YAML.load_file(obj) rescue {}
    end

    private :get_merged_settings, :get_dict, :write_to_file

end
