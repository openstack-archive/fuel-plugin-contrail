require 'yaml'

Puppet::Type.type(:ceilometer_pipeline_section).provide(:ruby) do

  attr_accessor :resource

  # Alias to the yaml file path
  # @return [String]
  def yaml_file_path
    resource[:path]
  end

  # Alias to the array name
  # @return [String]
  def array_name
    resource[:array_name]
  end

  # Alias to the section name
  # @return [String]
  def section_name
    resource[:section_name]
  end

  # The exiting data read from the YAML file
  # @return [Hash]
  def existing_data
    return @yaml_file_existing_data if @yaml_file_existing_data
    begin
      @yaml_file_existing_data = YAML.load_file resource[:path]
      fail "YAML data should be a hash in the file: '#{yaml_file_path}'!" unless @yaml_file_existing_data.is_a? Hash
      @yaml_file_existing_data
    rescue => exception
      warn "Could not read the YAML file: '#{yaml_file_path}' #{exception}"
      @yaml_file_existing_data = {}
    end
  end

  # Write the expected data to the YAML file
  def yaml_file_write
    File.open(yaml_file_path, 'w') do |file|
      file.puts YAML.dump expected_data
    end
  end

  # The expected YAML data with updated hardware_source section
  # @return [Hash]
  def expected_data
    return @yaml_file_expected_data if @yaml_file_expected_data
    @yaml_file_expected_data = Marshal.load Marshal.dump existing_data
    @yaml_file_expected_data[array_name] = [] unless @yaml_file_expected_data[array_name]
    if resource[:ensure] == :present
      modify_section @yaml_file_expected_data
    else
      remove_section @yaml_file_expected_data
    end
    @yaml_file_expected_data
  end

  # Update the selected section in the
  # provided YAML data or add a new section if
  # it's missing.
  # @param [Hash] data
  def modify_section(data)
    sources = data.fetch array_name, []
    target_section = section data
    if target_section
      target_section.clear
      target_section.merge! resource[:data]
      target_section['name'] = section_name
    else
      sources << new_section
    end
    sources
  end

  # Extract rhe hardware_source section from the data
  # @param [Hash] data
  # @return [Hash]
  def section(data)
    sources = data.fetch array_name, []
    sources.find do |source|
      next unless source.is_a? Hash
      source['name'] == section_name
    end
  end

  # Remove the hardware_source section from the data
  # @param [Hash] data
  def remove_section(data)
    sources = data.fetch array_name, []
    sources.reject! do |source|
      source['name'] == section_name
    end
    sources
  end

  # Generate a new hardware_source section
  # @return [Hash]
  def new_section
    section = resource[:data]
    section['name'] = section_name
    section
  end

  #####

  def exists?
    if resource[:ensure] == :absent
      !section(existing_data).nil?
    else
      existing_data == expected_data
    end
  end

  def create
    yaml_file_write
  end

  def destroy
    yaml_file_write
  end

end
