require 'spec_helper'

describe Puppet::Type.type(:ceilometer_pipeline_section) do

  subject do
    Puppet::Type.type(:ceilometer_pipeline_section)
  end

  it 'should exist' do
    is_expected.not_to be_nil
  end

  describe 'basic structure' do
    it 'should be able to create an instance' do
      expect(subject.new(
          :name => 'test',
          :path => '/tmp/test.yaml',
      )).to_not be_nil
    end

    [:name, :path, :array_name, :section_name, :data].each do |param|
      it "should have a #{param} parameter" do
        expect(subject.validparameter?(param)).to be_truthy
      end

      it "should have documentation for its #{param} parameter" do
        expect(subject.paramclass(param).doc).to be_a String
      end
    end

  end
end
