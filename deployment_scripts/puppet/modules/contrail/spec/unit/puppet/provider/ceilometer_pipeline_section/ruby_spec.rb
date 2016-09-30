require 'spec_helper'

describe Puppet::Type.type(:ceilometer_pipeline_section).provider(:ruby) do

  let(:section_data) do
    {
        'name' => 'contrail_source',
        'a' => '1',
        'b' => {
            'c' => [1, 2, 3],
            'd' => '2',
        }
    }
  end

  let(:resource) do
    Puppet::Type.type(:ceilometer_pipeline_section).new(
        :name => 'test',
        :path => '/tmp/test.yaml',
        :data => section_data,
        :provider => :ruby,
    )
  end

  let(:provider) do
    resource.provider
  end

  subject { provider }

  it { is_expected.not_to be_nil }

  def get_source(data, name)
    data['sources'].find { |host| host['name'] == name }
  end

  context 'data modification' do

    it 'can add a new section with a custom data' do
      data = {'sources' => []}
      subject.modify_section data
      expect(get_source data, 'contrail_source').to eq(section_data)
    end

    it 'can update the existing section with a custom data' do
      data = {
          'sources' => [
              {
                  'name' => 'contrail_source',
                  'a' => '1',
              }

          ]
      }
      subject.modify_section data
      expect(get_source data, 'contrail_source').to eq(section_data)
    end

  end

end
