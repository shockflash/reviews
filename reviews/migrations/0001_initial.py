# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Category'
        db.create_table('reviews_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
        ))
        db.send_create_signal('reviews', ['Category'])

        # Adding model 'CategorySegment'
        db.create_table('reviews_categorysegment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('position', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['reviews.Category'])),
        ))
        db.send_create_signal('reviews', ['CategorySegment'])

        # Adding model 'Review'
        db.create_table('reviews_review', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='content_type_set_for_review', to=orm['contenttypes.ContentType'])),
            ('object_pk', self.gf('django.db.models.fields.CharField')(max_length=2000)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='review_reviews', null=True, to=orm['auth.User'])),
            ('user_name', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('user_email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('text', self.gf('django.db.models.fields.TextField')(max_length=3000)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('rating', self.gf('django.db.models.fields.IntegerField')()),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['reviews.Category'])),
            ('submit_date', self.gf('django.db.models.fields.DateTimeField')(default=None)),
            ('ip_address', self.gf('django.db.models.fields.IPAddressField')(max_length=15, null=True, blank=True)),
            ('is_public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('is_removed', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('reviews', ['Review'])

        # Adding model 'ReviewFlag'
        db.create_table('reviews_reviewflag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='review_flags', to=orm['auth.User'])),
            ('review', self.gf('django.db.models.fields.related.ForeignKey')(related_name='flags', to=orm['reviews.Review'])),
            ('flag', self.gf('django.db.models.fields.CharField')(max_length=30, db_index=True)),
            ('flag_date', self.gf('django.db.models.fields.DateTimeField')(default=None)),
        ))
        db.send_create_signal('reviews', ['ReviewFlag'])

        # Adding unique constraint on 'ReviewFlag', fields ['user', 'review', 'flag']
        db.create_unique('reviews_reviewflag', ['user_id', 'review_id', 'flag'])

        # Adding model 'ReviewSegment'
        db.create_table('reviews_reviewsegment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('review', self.gf('django.db.models.fields.related.ForeignKey')(related_name='segments', to=orm['reviews.Review'])),
            ('rating', self.gf('django.db.models.fields.IntegerField')()),
            ('text', self.gf('django.db.models.fields.TextField')(max_length=3000)),
            ('segment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['reviews.CategorySegment'])),
        ))
        db.send_create_signal('reviews', ['ReviewSegment'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'ReviewFlag', fields ['user', 'review', 'flag']
        db.delete_unique('reviews_reviewflag', ['user_id', 'review_id', 'flag'])

        # Deleting model 'Category'
        db.delete_table('reviews_category')

        # Deleting model 'CategorySegment'
        db.delete_table('reviews_categorysegment')

        # Deleting model 'Review'
        db.delete_table('reviews_review')

        # Deleting model 'ReviewFlag'
        db.delete_table('reviews_reviewflag')

        # Deleting model 'ReviewSegment'
        db.delete_table('reviews_reviewsegment')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'reviews.category': {
            'Meta': {'object_name': 'Category'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'reviews.categorysegment': {
            'Meta': {'object_name': 'CategorySegment'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['reviews.Category']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'reviews.review': {
            'Meta': {'ordering': "('submit_date',)", 'object_name': 'Review'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['reviews.Category']"}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'content_type_set_for_review'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_removed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'object_pk': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            'rating': ('django.db.models.fields.IntegerField', [], {}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'submit_date': ('django.db.models.fields.DateTimeField', [], {'default': 'None'}),
            'text': ('django.db.models.fields.TextField', [], {'max_length': '3000'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'review_reviews'", 'null': 'True', 'to': "orm['auth.User']"}),
            'user_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'user_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'})
        },
        'reviews.reviewflag': {
            'Meta': {'unique_together': "[('user', 'review', 'flag')]", 'object_name': 'ReviewFlag'},
            'flag': ('django.db.models.fields.CharField', [], {'max_length': '30', 'db_index': 'True'}),
            'flag_date': ('django.db.models.fields.DateTimeField', [], {'default': 'None'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'review': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'flags'", 'to': "orm['reviews.Review']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'review_flags'", 'to': "orm['auth.User']"})
        },
        'reviews.reviewsegment': {
            'Meta': {'object_name': 'ReviewSegment'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rating': ('django.db.models.fields.IntegerField', [], {}),
            'review': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'segments'", 'to': "orm['reviews.Review']"}),
            'segment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['reviews.CategorySegment']"}),
            'text': ('django.db.models.fields.TextField', [], {'max_length': '3000'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['reviews']
